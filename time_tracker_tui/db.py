import os
from typing import List, Tuple

import sqlite3
from platformdirs import user_data_dir

from .definition import ROOT_PKG_DIR


DB_NAME = "time.db"
USER_DATA_DIR = user_data_dir("time-tracker-tui")

table_name = "sessions"


def _init_db() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def _table_exists() -> bool:
    cur.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{table_name}'"
    )
    return True if cur.fetchall() else False


def _create_total_table() -> None:
    cur.execute(
            "CREATE TABLE tt0 AS "
            "SELECT s.task, sum(s.time) as total "
            f"FROM {table_name} s "
            "GROUP BY s.task "
            "ORDER BY s.id"
    )
    conn.commit()


def _create_today_table() -> None:
    cur.execute(
            "CREATE TABLE tt1 AS "
            "SELECT s.task, sum(s.time) as today "
            f"FROM {table_name} s "
            "WHERE s.date = date('now') "
            "GROUP BY s.task"
    )
    conn.commit()


def _create_month_table() -> None:
    cur.execute(
            "CREATE TABLE tt2 AS "
            "SELECT s.task, sum(s.time) as month "
            f"FROM {table_name} s "
            "WHERE s.date LIKE strftime('%Y-%m-%%', 'now') "
            "GROUP BY s.task"
    )
    conn.commit()


def _drop_temp_tables() -> None:
    try:
        cur.execute("DROP TABLE tt0")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("DROP TABLE tt1")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("DROP TABLE tt2")
    except sqlite3.OperationalError:
        pass
    conn.commit()


def fetch_full_info() -> List[Tuple]:
    _drop_temp_tables()
    _create_total_table()
    _create_today_table()
    _create_month_table()
    cur.execute(
            "SELECT tt0.task, tt1.today, tt2.month, tt0.total "
            "FROM tt0 "
            "LEFT OUTER JOIN tt1 "
            "ON tt0.task = tt1.task "
            "LEFT OUTER JOIN tt2 "
            "ON tt0.task = tt2.task"
    )
    result = cur.fetchall()
    _drop_temp_tables()
    return result


def insert_session(task: str, date: str, time: int) -> None:
    cur.execute(
        f"INSERT INTO {table_name} (task, date, time) "
        f"VALUES ('{task}', '{date}', {time})"
    )
    conn.commit()


def delete_task(task: str) -> None:
    cur.execute(f"DELETE FROM {table_name} WHERE task = '{task}'")
    conn.commit()


def _create_dirs(path: str) -> None:
    if not os.path.exists(path):
        _create_dirs(os.path.dirname(path))
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


_create_dirs(USER_DATA_DIR)

conn = sqlite3.connect(os.path.join(USER_DATA_DIR, DB_NAME))
cur = conn.cursor()

if not _table_exists():
    _init_db()
