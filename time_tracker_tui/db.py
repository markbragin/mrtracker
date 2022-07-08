import os
from typing import List, Tuple

import sqlite3
from loguru import logger
from platformdirs import user_data_dir

from .definition import ROOT_PKG_DIR


DB_NAME = "test.db"
USER_DATA_DIR = user_data_dir("time-tracker-tui")


def _init_db() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def _check_db_exists() -> bool:
    return os.path.exists(USER_DATA_DIR)


def _create_total_table() -> None:
    cur.execute(
        "CREATE TEMP TABLE tt0 AS "
        "SELECT s.task_id, sum(s.time) as total "
        "FROM sessions s "
        "GROUP BY s.task_id "
        "ORDER BY s.id DESC"
    )
    conn.commit()


def _create_today_table() -> None:
    cur.execute(
        "CREATE TEMP TABLE tt1 AS "
        "SELECT s.task_id, sum(s.time) as today "
        "FROM sessions s "
        "WHERE s.date = date('now', 'localtime') "
        "GROUP BY s.task_id"
    )
    conn.commit()


def _create_month_table() -> None:
    cur.execute(
        "CREATE TEMP TABLE tt2 AS "
        "SELECT s.task_id, sum(s.time) as month "
        "FROM sessions s "
        "WHERE s.date LIKE strftime('%Y-%m-%%', 'now') "
        "GROUP BY s.task_id"
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
    _create_total_table()
    _create_today_table()
    _create_month_table()
    cur.execute(
        "SELECT t.id, l.parent_id, t.name, tt1.today, tt2.month, tt0.total "
        "FROM tasks t "
        "LEFT OUTER JOIN tt0 "
        "ON t.id = tt0.task_id "
        "LEFT OUTER JOIN tt1 "
        "ON t.id = tt1.task_id "
        "LEFT OUTER JOIN tt2 "
        "ON t.id = tt2.task_id "
        "LEFT OUTER JOIN links l "
        "ON t.id = l.task_id "
        "WHERE id > 0"
    )
    result = cur.fetchall()
    _drop_temp_tables()
    return result


def add_session(task_id: int, date: str, time: int) -> None:
    cur.execute(
        f"INSERT INTO sessions (task_id, date, time) "
        f"VALUES ('{task_id}', '{date}', {time})"
    )
    conn.commit()


def add_task(task: str, parent_id: int = 0) -> None:
    cur.execute(f"INSERT INTO tasks (name) VALUES ('{task}')")
    cur.execute("SELECT id from tasks "
                "WHERE id = (SELECT MAX(id) from tasks)")
    task_id = cur.fetchone()[0]
    cur.execute(f"INSERT INTO links VALUES ({task_id}, {parent_id})")
    conn.commit()


def delete_tasks(*tasks: int) -> None:
    task_ids = ", ".join(str(x) for x in tasks)
    cur.execute(f"DELETE FROM tasks WHERE id in ({task_ids})")
    conn.commit()


def rename_task(id: int, new_name: str) -> None:
    cur.execute(f"UPDATE tasks SET name = '{new_name}' WHERE id={id}")
    conn.commit()


def get_max_task_id() -> int:
    cur.execute("SELECT MAX(id) from tasks")
    return cur.fetchone()[0]


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

if not _check_db_exists():
    _init_db()

cur.execute("PRAGMA foreign_keys=ON")
conn.commit()
