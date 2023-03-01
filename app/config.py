import json
import os
from . import globals


def load_config():
    try:
        with open(globals.CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def create_config(config):

    if not os.path.exists(globals.DATA_DIR):
        os.makedirs(globals.DATA_DIR)

    with open(globals.CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


def reload():
    global config
    config = load_config()
    if not config:
        template = {
            "token": "",
            "prefix": "$",
            "discordDelay": 100,
            "updateLink": "",
            "scanDays": 30,
            "updateDelay": 3600,
            "updateSpreadsheetName": "Data",
            "submitChannel": "",
            "adminChannel": "",
            "testChannel": "",
            "updateChannels": [
                ""
            ],
            "admins": [
                ""
            ],
            "roles": [
                {
                    "name": "TS",
                    "value": 2.5
                }
            ]
        }
        print("El archivo de configuración no existe.")
        print("Por favor llena el archivo 'config.json' que fue creado con los valores correspondientes:")
        print(template)
        create_config(template)
        exit(0)
