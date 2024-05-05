import ctypes


def lock_screen():
    user32 = ctypes.windll.User32
    user32.LockWorkStation()
