import json


def get_current_volume():
    with open('volume.json', mode='r+') as file:
        data = json.load(file)
        current_volume = data["volume"]
        return current_volume
