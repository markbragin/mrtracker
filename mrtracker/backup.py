import os
import shutil

from .config import DB_PATH, generate_backup_name


def create_backup(path: str) -> str:
    """Creates backup and returns its location"""
    if os.path.isdir(path):
        dump_path = os.path.join(path, generate_backup_name())
    elif os.path.isdir(os.path.dirname(path)):
        dump_path = path
    else:
        dump_path = os.path.join(".", path)
    shutil.copy(DB_PATH, path)
    return os.path.abspath(dump_path)


def restore_data(path: str) -> None:
    """Replaces all the data with the data from backup"""
    shutil.copy(path, DB_PATH)
