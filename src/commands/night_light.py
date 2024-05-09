import winreg

STATUS_PATH = r"Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate"
STATE_VALUE_NAME = "Data"


def get_night_light_state_data():
    try:
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATUS_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(hKey, STATE_VALUE_NAME)
        winreg.CloseKey(hKey)

        if regtype == winreg.REG_BINARY:
            return value
    except:
        pass
    return False


def process_night_light_state_data(byte_array):
    night_light_is_on = False
    ch = byte_array[18]
    size = len(byte_array)

    if ch == 0x15:
        night_light_is_on = True
        for i in range(10, 15):
            ch = byte_array[i]
            if ch != 0xff:
                byte_array[i] += 1
                break
        byte_array[18] = 0x13
        for i in range(24, 22, -1):
            for j in range(i, size - 2):
                byte_array[j] = byte_array[j + 1]
    elif ch == 0x13:
        night_light_is_on = False
        for i in range(10, 15):
            ch = byte_array[i]
            if ch != 0xff:
                byte_array[i] += 1
                break
        byte_array[18] = 0x15
        n = 0
        while n < 2:
            for j in range(size - 1, 23, -1):
                byte_array[j] = byte_array[j - 1]
            n += 1
        byte_array[23] = 0x10
        byte_array[24] = 0x00
        # extend array
        ba = bytearray(1)
        ba[0] = 0x00
        byte_array.extend(ba)
        byte_array.extend(ba)
    return night_light_is_on


def write_data_to_registry(byte_array, night_light_state):
    size = len(byte_array)
    retval = False
    try:
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATUS_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(hKey, STATE_VALUE_NAME, 0, winreg.REG_BINARY, byte_array[:size])
        winreg.CloseKey(hKey)
        retval = True
    except:
        pass
    return retval


def run_night_light_process():
    night_light_is_on = False
    value = get_night_light_state_data()
    size = len(value)
    reg_val = bytearray(size)
    reg_val[:] = value
    if get_night_light_state_data():
        night_light_new_settings = process_night_light_state_data(reg_val)
        write_data_to_registry(reg_val, night_light_new_settings)
