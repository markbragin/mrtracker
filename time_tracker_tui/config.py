import json
import os
import shutil

from platformdirs import user_config_dir, user_data_dir


ROOT_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = "time-tracker-tui"
CONFIG_FILE = "config.json"
EXAMPLE_CONFIG_FILE = "example_config.json"
USER_CONFIG_DIR = user_config_dir(APP_DIR)
USER_DATA_DIR = user_data_dir(APP_DIR)
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
        self.read_config()

    def read_config(self) -> None:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            self.bindings = cfg["bindings"]
            self.styles = cfg["styles"]


create_dirs(USER_DATA_DIR)
config = Config()
