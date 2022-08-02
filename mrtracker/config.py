import json
import os
import shutil

from platformdirs import user_config_dir, user_data_dir


ROOT_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "mrtracker"
CONFIG_FILE = "config.json"
BASE_CONFIG_FILE = "default_config.json"
DATA_DIR = user_data_dir(APP_NAME)
CONFIG_DIR = user_config_dir(APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILE)
BASE_CONFIG_PATH = os.path.join(ROOT_PKG_DIR, BASE_CONFIG_FILE)

DB_NAME = "time.db"
DB_VERSION = 1


def create_dirs(path: str) -> None:
    if not os.path.exists(path):
        create_dirs(os.path.dirname(path))
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


class Config:
    def __init__(self) -> None:
        self.load_config()

    def copy_base_config(self) -> None:
        create_dirs(CONFIG_DIR)
        shutil.copy(BASE_CONFIG_PATH, CONFIG_PATH)

    def load_config(self) -> None:
        if not os.path.exists(CONFIG_PATH):
            self.copy_base_config()
        else:
            self.merge_configs()
        self.read_config()

    def merge_configs(self) -> None:
        with open(CONFIG_PATH, "r") as f1:
            user = json.load(f1)
        with open(BASE_CONFIG_PATH, "r") as f:
            base = json.load(f)

        for section in base:
            if section == "help" or section not in user:
                continue
            for key in base[section]:
                if key in user[section]:
                    base[section][key] = user[section][key]

        with open(CONFIG_PATH, "w") as f1:
            json.dump(base, f1, indent=4)

    def read_config(self) -> None:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            self.app_keys = cfg["app_keys"]
            self.tasklist_keys = cfg["tasklist_keys"]
            self.stats_keys = cfg["stats_keys"]
            self.styles = cfg["styles"]


create_dirs(DATA_DIR)
config = Config()
