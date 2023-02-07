import json


def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def create_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file)


config = load_config()
if not config:
    print("El archivo de configuración no existe.")
    print("Por favor llena el archivo 'config.json' que fue creado con los valores correspondientes")
    create_config({
        "token": "",
        "sheet_name": "CyanBot"
    })
    exit(1)
