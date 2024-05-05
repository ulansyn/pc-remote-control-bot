import os


def shutdown():
    os.system(f"shutdown /s /t 1")


def reboot():
    os.system(f"shutdown /r /t 1")


def sleep_mode():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


def hibernation_mode():
    os.system("shutdown /h")


def cancel_shutdown():
    os.system("shutdown /a")
