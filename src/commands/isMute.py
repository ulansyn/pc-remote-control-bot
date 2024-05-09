from commands.current_volume import get_current_volume
def is_mute():
    return get_current_volume() == 0