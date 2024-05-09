from time import sleep
import os



def shutdown():
    os.system(f"shutdown /s /t 1")


def reboot():
    os.system(f"shutdown /r /t 1")


def sleep_mode():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


def hibernation_mode():
    os.system("shutdown /h")


def lock_screen(seconds=1):
    os.system("rundll32.exe user32.dll,LockWorkStation")

def execute_command(command, ):
    actions = {'/shutdown':shutdown,
               '/reboot':reboot,
               '/sleep_mode':sleep_mode,
               '/hibernation_mode':hibernation_mode,
               '/lock_screen':lock_screen,
               }
    actions[command]()
def power_control(command):
    try:
        execute_command(command)
    except Exception as e:
        print('Что-то пошло не так:', e)