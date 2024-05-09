import re
import telebot
import threading
import configparser
from telebot import types, apihelper
from commands.power_control import *
from commands.actions import ACTIONS
from commands.isMute import is_mute
from commands.open_link import open_link
from commands.get_screenshot import get_screenshot
from commands.youtube_search import youtube_search
from commands.change_wallpaper import change_wallpaper
from commands.current_volume import get_current_volume
from commands.night_light import run_night_light_process
from commands.volume_control import decrease_volume, STEP, increase_volume


def timer(bot, USER_ID, command, delay, func, shutdown_flag):
    msg = bot.send_message(USER_ID, f"{ACTIONS[command]} через {delay} секунд")
    if delay > 1:
        for i in range(delay - 1, 0, -1):
            if shutdown_flag.is_set():  # Проверяем, была ли установлена команда на отмену
                print("Поток был остановлен по команде отмены.")
                bot.edit_message_text(f"Таймер остановлен", USER_ID, msg.message_id)
                return
            bot.edit_message_text(f"{ACTIONS[command]} через {i} секунд", USER_ID, msg.message_id)
            sleep(1)
    bot.edit_message_text(f"{ACTIONS[command]}", USER_ID, msg.message_id)
    sleep(1)
    func(command)


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

TOKEN = config['Telegram']['bot_token']
USER_ID = config['User_id']['id']
WALLPAPERS_PATH = config['Wallpapers_path']['wallpapers_path']
bot = telebot.TeleBot(TOKEN)
apihelper.CONNECT_TIMEOUT = 100  # Connect timeout
apihelper.READ_TIMEOUT = 200
shutdown_flag = threading.Event()


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """Все команды:
/volume_control - Управление громкостью
/shutdown <code>&lt;seconds&gt;</code> - выключить ПК
/reboot <code>&lt;seconds&gt;</code> - перезагрузить ПК
/sleep_mode <code>&lt;seconds&gt;</code> - переход в спящий режим
/hibernation_mode <code>&lt;seconds&gt;</code> - переход в режим гибернации
/cancel_shutdown - отмена таймера
/lock_screen - блокировка ПК
/night_light - переключить ночной свет
/get_screenshot - получить скриншот
/youtube <code>&lt;link&gt;</code> - открыть youtube

&lt;&gt; - необязательный аргумент""", parse_mode="HTML")


@bot.message_handler(commands=['youtube'])
def youtube(message):
    if message.text == '/youtube':
        open_link('https://www.youtube.com/')
    else:
        open_link(youtube_search(message.text[8:]))


@bot.message_handler(commands=['get_screenshot'])
def send_screenshot(message):
    with open(get_screenshot(), 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['night_light'])
def night_light(message):
    run_night_light_process()


@bot.message_handler(
    commands=['shutdown', 'reboot', 'sleep_mode', 'hibernation_mode', 'cancel_shutdown', 'lock_screen'])
def handle_power_command(message):
    global shutdown_flag

    try:
        command, *args = message.text.split()
        delay = int(args[0]) if args else 1
        if command == '/cancel_shutdown':
            shutdown_flag.set()  # Устанавливаем флаг остановки потока
            print('Поток остановлен')
            return
        if delay == 1:
            confirmation_keyboard = types.InlineKeyboardMarkup()  # Создаем клавиатуру для подтверждения
            confirm_button = types.InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{command}")
            cancel_button = types.InlineKeyboardButton("Отмена", callback_data=f"cancel_{command}")
            confirmation_keyboard.add(confirm_button, cancel_button)
            bot.send_message(message.chat.id, "Подтвердите действие:", reply_markup=confirmation_keyboard)
        else:

            threading.Thread(target=timer, args=(bot, USER_ID, command, delay, power_control, shutdown_flag)).start()
            shutdown_flag.clear()  # Сбрасываем флаг остановки потока перед запуском нового потока

    except Exception as e:
        print('Ошибка обработки команды питания:', e)


first_message_id = None  # Глобальная переменная для хранения идентификатора первого сообщения


@bot.message_handler(commands=['volume_control'])
def handle_volume_control(message):
    global first_message_id  # Используем глобальную переменную

    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("◀️ Уменьшить", callback_data='button1')
    button2 = types.InlineKeyboardButton("Увеличить ▶️", callback_data='button2')
    mute_button_text = "Выключить звук" if not is_mute() else "Включить звук"
    button3 = types.InlineKeyboardButton(mute_button_text, callback_data='button3')
    keyboard.add(button1, button2, button3)

    # Отправляем сообщение с текущей громкостью и клавиатурой
    msg = bot.send_message(USER_ID, f"Текущая громкость: {get_current_volume()}", reply_markup=keyboard)

    # Сохраняем идентификатор первого сообщения
    first_message_id = msg.message_id


@bot.message_handler(commands=['change_wallpaper'])
def change_wallpaper_(message):
    change_wallpaper(WALLPAPERS_PATH)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    global first_message_id

    def update_volume_message():
        # Обновляем сообщение с текущей громкостью и клавиатурой
        keyboard = update_keyboard()
        bot.edit_message_text(f"Текущая громкость: {get_current_volume()}",
                              chat_id=USER_ID, message_id=first_message_id,
                              reply_markup=keyboard)

    def update_keyboard():
        # Обновляем клавиатуру в зависимости от состояния звука
        mute_status = is_mute()
        mute_button_text = "Выключить звук" if not mute_status else "Включить звук"
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("◀️ Уменьшить", callback_data='button1')
        button2 = types.InlineKeyboardButton("Увеличить ▶️", callback_data='button2')
        button3 = types.InlineKeyboardButton(mute_button_text, callback_data='button3')
        keyboard.add(button1, button2, button3)
        return keyboard

    # Обработка нажатий на кнопки
    if call.data == "button1":
        decrease_volume(STEP)
        bot.answer_callback_query(call.id, "Громкость уменьшена")
        update_volume_message()
    elif call.data == "button2":
        increase_volume(STEP)
        bot.answer_callback_query(call.id, "Громкость увеличена")
        update_volume_message()
    elif call.data == 'button3':
        if is_mute():
            increase_volume(20)  # Установите это значение для "включения" звука

        else:
            decrease_volume(get_current_volume())  # Полное выключение звука

        bot.answer_callback_query(call.id, "Статус звука изменен")
        update_volume_message()
    if call.data.split('/')[0] == 'confirm_':
        command = '/' + call.data.split('/')[-1]
        bot.send_message(USER_ID, 'Действие подтверждено')
        bot.answer_callback_query(call.id, text="")
        threading.Thread(target=timer, args=(bot, USER_ID, command, 0, power_control, shutdown_flag)).start()
        shutdown_flag.clear()
    elif call.data.split('/')[0] == 'cancel_':
        bot.send_message(USER_ID, 'Действие отменено')
        bot.answer_callback_query(call.id, text="")


@bot.message_handler(func=lambda message: True)
def send_file_or_dir(message):
    path = message.text
    if os.path.exists(path):
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                bot.send_document(message.chat.id, file)
        elif os.path.isdir(path):
            file_list = os.listdir(path)
            # Экранируем символы Markdown
            path = re.sub(r'([\[\]()])', r'\\\1', path)
            file_list = ["`\n" + path + "/" + i + "`" + '\n' for i in file_list]
            bot.reply_to(message, "Содержимое текущей директории:\n" + "".join(file_list), parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, "Ошибка! Вы пытаетесь найти файл или директорию которого нет")


bot.polling()
