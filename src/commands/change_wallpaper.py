import os
import random
import ctypes

def change_wallpaper(folder_path):
    try:
        if not os.path.isdir(folder_path):
            print(f"Ошибка: '{folder_path}' не является директорией.")
            return

        image_files = [f for f in os.listdir(folder_path) if
                       f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        if not image_files:
            print(f"Ошибка: в директории '{folder_path}' нет изображений для установки в качестве обоев.")
            return

        random_wallpaper = random.choice(image_files)
        wallpaper_path = os.path.join(folder_path, random_wallpaper)

        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)
        print(f"Успешно установлены обои рабочего стола: {wallpaper_path}")
    except Exception as e:
        print(f"Произошла ошибка при установке обоев: {e}")