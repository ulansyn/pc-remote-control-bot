import os


def send_file_or_dir_path(path):
    """Для С: надо ввести С:\\ или С:/"""
    if os.path.exists(path):
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            file_list = os.listdir(path)
            return "\n".join(file_list)
    else:
        return "Не найдено"
