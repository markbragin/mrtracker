import json
import os
import shutil

from jsonmerge import merge
from platformdirs import user_config_dir, user_data_dir


ROOT_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "mrtracker"
CONFIG_FILE = "config.json"
EXAMPLE_CONFIG_FILE = "default_config.json"
USER_CONFIG_DIR = user_config_dir(APP_NAME)
USER_DATA_DIR = user_data_dir(APP_NAME)
CONFIG_PATH = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)
EXAMPLE_CONFIG_PATH = os.path.join(ROOT_PKG_DIR, EXAMPLE_CONFIG_FILE)

DB_NAME = "time.db"


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

    def copy_example_config(self) -> None:
        create_dirs(USER_CONFIG_DIR)
        shutil.copy(EXAMPLE_CONFIG_PATH, CONFIG_PATH)

    def load_config(self) -> None:
        if not os.path.exists(CONFIG_PATH):
            self.copy_example_config()
        else:
            self.merge_configs()
        self.read_config()

    def merge_configs(self) -> None:
        with open(CONFIG_PATH, "r") as f1:
            with open(EXAMPLE_CONFIG_PATH, "r") as f2:
                user = json.load(f1)
                base = json.load(f2)
        with open(CONFIG_PATH, "w") as f1:
            json.dump(merge(base, user), f1, indent=4)

    def read_config(self) -> None:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            self.app_keys = cfg["bindings"]["app"]
            self.tasklist_keys = cfg["bindings"]["tasklist"]
            self.styles = cfg["styles"]


create_dirs(USER_DATA_DIR)
config = Config()
