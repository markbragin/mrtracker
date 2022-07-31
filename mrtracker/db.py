from datetime import datetime, timedelta
import os
import sqlite3

from .config import DB_NAME, ROOT_PKG_DIR, DATA_DIR


def _init_db() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def _check_db_exists() -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return cur.fetchone()


def fetch_tasks() -> list[tuple]:
    cur.execute(
        "SELECT t.id, p.id, t.name, SUM(s.time) "
        "FROM tasks t "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "LEFT JOIN sessions s "
        "ON t.id = s.task_id "
        "GROUP BY t.id"
    )
    return cur.fetchall()


def fetch_projects() -> list[tuple]:
    cur.execute("SELECT id, NULL, name, NULL FROM projects ")
    return cur.fetchall()


def fetch_today() -> list[tuple]:
    cur.execute(
        "SELECT t.name, SUM(s.time) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE date = date('now', 'localtime') "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC"
    )
    return cur.fetchall()


def fetch_week() -> list[tuple]:
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    cur.execute(
        "SELECT t.name, SUM(s.time) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC",
        (week_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_month() -> list[tuple]:
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    cur.execute(
        "SELECT t.name, SUM(s.time) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC",
        (month_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def add_session(task_id: int, date: str, time: int) -> None:
    cur.execute(
        "INSERT INTO sessions (task_id, date, time) VALUES (?, ?, ?)",
        (task_id, date, time),
    )
    conn.commit()


def add_project(name: str) -> None:
    cur.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()


def add_task(name: str, project_id: int) -> None:
    cur.execute(
        "INSERT INTO tasks (name, project_id) VALUES (?, ?)",
        (name, project_id),
    )
    conn.commit()


def delete_project(project_id: int) -> None:
    cur.execute("DELETE FROM projects WHERE id=(?)", (project_id,))
    conn.commit()


def delete_task(task_id: int) -> None:
    cur.execute("DELETE FROM tasks WHERE id=(?)", (task_id,))
    conn.commit()


def rename_project(project_id: int, new_name: str) -> None:
    cur.execute(
        "UPDATE projects SET name = (?) WHERE id=(?)",
        (new_name, project_id),
    )
    conn.commit()


def rename_task(task_id: int, new_name: str) -> None:
    cur.execute(
        "UPDATE tasks SET name = (?) WHERE id=(?)",
        (new_name, task_id),
    )
    conn.commit()


def change_project(task_id: int, new_project_id: int) -> None:
    cur.execute(
        "UPDATE tasks SET project_id = (?) WHERE id=(?)",
        (new_project_id, task_id),
    )
    conn.commit()


def delete_sessions_by_task_ids(task_ids: list[int]) -> None:
    placeholders = ", ".join("?" for _ in task_ids)
    cur.execute(
        "DELETE FROM sessions WHERE task_id in (%s)" % placeholders, task_ids
    )
    conn.commit()


def get_next_task_id() -> int:
    cur.execute("SELECT MAX(id) FROM tasks")
    return cur.fetchone()[0] + 1


def get_next_project_id() -> int:
    cur.execute("SELECT MAX(id) FROM projects")
    return cur.fetchone()[0] + 1


conn = sqlite3.connect(os.path.join(DATA_DIR, DB_NAME))
cur = conn.cursor()

if not _check_db_exists():
    _init_db()

cur.execute("PRAGMA foreign_keys=ON")
conn.commit()
