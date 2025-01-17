import re
import json
from pathlib import Path

CAMERAS_PATH = Path("cameras.json")


# Функция для чтения JSON из файла
def read_json():
    with open(CAMERAS_PATH, "r") as f:
        return json.load(f)


# Функция для записи JSON в файл
def write_json(data):
    with open(CAMERAS_PATH, "w") as f:
        json.dump(data, f, indent=4)


def update_config(camera_script_path, script_name):
    try:
        with open(camera_script_path, "r") as f:
            data = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    try:
        name_pattern = r'\bname:\s*"[^"]*"'
        args_pattern = r'\bargs:\s*"[^"]*"'
        new_name_data = re.sub(name_pattern, f'name: "{script_name}"', data)
        result_data = re.sub(args_pattern, f'args: "{script_name}.sh"', new_name_data)
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        return

    try:
        with open(camera_script_path, "w") as f:
            f.write(result_data)
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")


def create_new_config(template_path, new_path, script_name):
    try:
        with open(template_path, "r") as f:
            data = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    try:
        name_pattern = r'\bname:\s*"[^"]*"'
        args_pattern = r'\bargs:\s*"[^"]*"'
        new_name_data = re.sub(name_pattern, f'name: "{script_name}"', data)
        result_data = re.sub(args_pattern, f'args: "{script_name}.sh"', new_name_data)
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        return

    try:
        with open(new_path, "w") as f:
            f.write(result_data)
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")
