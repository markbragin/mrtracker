import csv
import os
import shutil

from .config import DB_PATH, generate_backup_name, generate_csv_name
from .db import Database


def create_backup(path: str) -> str:
    """Creates backup and returns its location"""
    if os.path.isdir(path):
        backup_path = os.path.join(path, generate_backup_name())
    elif os.path.isdir(os.path.dirname(path)):
        backup_path = path
    else:
        backup_path = os.path.join(".", path)

    shutil.copy(DB_PATH, backup_path)
    return os.path.abspath(backup_path)


def restore_data(path: str) -> None:
    """Replaces all the data with the data from backup"""
    shutil.copy(path, DB_PATH)


def create_csv(path: str) -> str:
    """Creates csv file and returns its location"""
    if os.path.isdir(path):
        csv_path = os.path.join(path, generate_csv_name())
    elif os.path.isdir(os.path.dirname(path)):
        csv_path = path
    else:
        csv_path = os.path.join(".", path)

    data = Database().fetch_for_csv()
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            (
                "project",
                "task",
                "tags",
                "date",
                "start time",
                "end time",
                "duration",
            )
        )
        writer.writerows(data)
    return os.path.abspath(csv_path)
