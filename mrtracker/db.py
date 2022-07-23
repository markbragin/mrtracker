import os
import sqlite3
from typing import List, Tuple

from .config import DB_NAME, ROOT_PKG_DIR, USER_DATA_DIR


def _init_db() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def _check_db_exists() -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return cur.fetchone()


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
        "INSERT INTO sessions (task_id, date, time) VALUES (?, ?, ?)",
        (task_id, date, time),
    )
    conn.commit()


def add_task(task: str, parent_id: int = 0) -> None:
    cur.execute("INSERT INTO tasks (name) VALUES (?)", (task,))
    cur.execute("SELECT id from tasks WHERE id = (SELECT MAX(id) from tasks)")
    task_id = cur.fetchone()[0]
    cur.execute("INSERT INTO links VALUES (?, ?)", (task_id, parent_id))
    conn.commit()


def delete_tasks(task_ids: list[int]) -> None:
    placeholders = ", ".join("?" for i in task_ids)
    cur.execute("DELETE FROM tasks WHERE id in (%s)" % placeholders, task_ids)
    conn.commit()


def rename_task(id: int, new_name: str) -> None:
    cur.execute("UPDATE tasks SET name = (?) WHERE id=(?)", (new_name, id))
    conn.commit()


def get_max_task_id() -> int:
    cur.execute("SELECT MAX(id) from tasks")
    return cur.fetchone()[0]


conn = sqlite3.connect(os.path.join(USER_DATA_DIR, DB_NAME))
cur = conn.cursor()

if not _check_db_exists():
    _init_db()

cur.execute("PRAGMA foreign_keys=ON")
conn.commit()
