import json
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
STEP = 5

if not os.path.exists('volume.json'):
    with open('volume.json', 'w') as file:
        initial_data = {"volume": 50}
        json.dump(initial_data, file)


def update_volume(change):
    with open('volume.json', mode='r+') as file:
        data = json.load(file)
        current_volume = data["volume"]
        new_volume = current_volume + change
        if 0 <= new_volume <= 100:
            volume.SetMasterVolumeLevelScalar(new_volume / 100, None)
            data["volume"] = new_volume
            file.seek(0)
            json.dump(data, file)
            file.truncate()
            return new_volume
        return current_volume


def decrease_volume(step):
    return update_volume(-step)


def increase_volume(step):
    return update_volume(step)
