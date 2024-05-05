from PIL import ImageGrab


def get_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("PATH")
