import os

RUNNING = True

DATA_DIR = os.path.abspath("./data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
SERIES_FILE = os.path.join(DATA_DIR, "series.json")
ALLOWED_FILE = os.path.join(DATA_DIR, "allowed.json")
MSG_FILE = os.path.join(DATA_DIR, "msg.json")
