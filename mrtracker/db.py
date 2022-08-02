from datetime import datetime, timedelta
import os
import sqlite3

from .config import DATA_DIR, DB_NAME, ROOT_PKG_DIR


def fetch_tasks() -> list[tuple]:
    cur.execute(
        "SELECT t.id, p.id, t.name, SUM(s.duration), t.tags "
        "FROM tasks t "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "LEFT JOIN sessions s "
        "ON t.id = s.task_id "
        "GROUP BY t.id "
        "ORDER BY t.id"
    )
    return cur.fetchall()


def fetch_projects() -> list[tuple]:
    cur.execute(
        "SELECT id, NULL, name, NULL, NULL FROM projects p ORDER BY p.id"
    )
    return cur.fetchall()


def fetch_tasks_today() -> list[tuple]:
    cur.execute(
        "SELECT t.name, SUM(s.duration) sum, p.name "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date = date('now', 'localtime') "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC"
    )
    return cur.fetchall()


def fetch_tasks_week() -> list[tuple]:
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    cur.execute(
        "SELECT t.name, SUM(s.duration) sum, p.name "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC",
        (week_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_tasks_month() -> list[tuple]:
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    cur.execute(
        "SELECT t.name, SUM(s.duration) sum, p.name "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY s.task_id "
        "ORDER BY sum DESC",
        (month_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_projects_today() -> list[tuple]:
    cur.execute(
        "SELECT p.name, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date = date('now', 'localtime') "
        "GROUP BY p.id "
        "ORDER BY sum DESC"
    )
    return cur.fetchall()


def fetch_projects_week() -> list[tuple]:
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    cur.execute(
        "SELECT p.name, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY p.id "
        "ORDER BY sum DESC",
        (week_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_projects_month() -> list[tuple]:
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    cur.execute(
        "SELECT p.name, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "LEFT JOIN projects p "
        "ON t.project_id = p.id "
        "WHERE date BETWEEN (?) AND (?) "
        "GROUP BY p.id "
        "ORDER BY sum DESC",
        (month_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_tags_today() -> list[tuple]:
    cur.execute(
        "SELECT t.tags, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE t.tags IS NOT NULL AND date = date('now', 'localtime') "
        "GROUP BY t.tags "
        "ORDER BY sum DESC"
    )
    return cur.fetchall()


def fetch_tags_week() -> list[tuple]:
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    cur.execute(
        "SELECT t.tags, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE t.tags IS NOT NULL AND date BETWEEN (?) AND (?) "
        "GROUP BY t.tags "
        "ORDER BY sum DESC",
        (week_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def fetch_tags_month() -> list[tuple]:
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    cur.execute(
        "SELECT t.tags, SUM(s.duration) sum "
        "FROM sessions s "
        "LEFT JOIN tasks t "
        "ON t.id = s.task_id "
        "WHERE t.tags IS NOT NULL AND date BETWEEN (?) AND (?) "
        "GROUP BY t.tags "
        "ORDER BY sum DESC",
        (month_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
    )
    return cur.fetchall()


def add_session(
    task_id: int,
    date: str,
    start_time: str,
    end_time: str,
    duration: int,
) -> None:
    cur.execute(
        "INSERT INTO sessions (task_id, date, start_time, end_time, duration) "
        "VALUES (?, ?, ?, ?, ?)",
        (task_id, date, start_time, end_time, duration),
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


def update_tags(task_ids: list[int], tag: str | None) -> None:
    placeholders = ", ".join("?" for _ in task_ids)
    cur.execute(
        "UPDATE tasks SET tags=(?) WHERE id in (%s)" % placeholders,
        (tag, *task_ids),
    )
    conn.commit()


def change_project(task_id: int, new_project_id: int) -> None:
    cur.execute(
        "UPDATE tasks SET project_id = (?) WHERE id=(?)",
        (new_project_id, task_id),
    )
    conn.commit()


def swap_projects(id1: int, id2: int) -> None:
    cur.execute("UPDATE projects SET id=-1 WHERE id=(?)", (id1,))
    cur.execute("UPDATE projects SET id=(?) WHERE id=(?)", (id1, id2))
    cur.execute("UPDATE projects SET id=(?) WHERE id=-1", (id2,))
    conn.commit()


def swap_tasks(id1: int, id2: int) -> None:
    cur.execute("UPDATE tasks SET id=-1 WHERE id=(?)", (id1,))
    cur.execute("UPDATE tasks SET id=(?) WHERE id=(?)", (id1, id2))
    cur.execute("UPDATE tasks SET id=(?) WHERE id=-1", (id2,))
    conn.commit()


def delete_sessions_by_task_ids(task_ids: list[int]) -> None:
    placeholders = ", ".join("?" for _ in task_ids)
    cur.execute(
        "DELETE FROM sessions WHERE task_id in (%s)" % placeholders, task_ids
    )
    conn.commit()


def get_next_task_id() -> int:
    cur.execute("SELECT MAX(id) FROM tasks")
    id = cur.fetchone()[0]
    return id + 1 if id else 1


def get_next_project_id() -> int:
    cur.execute("SELECT MAX(id) FROM projects")
    id = cur.fetchone()[0]
    return id + 1 if id else 1


def _init_db() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def _update_db() -> None:
    cur.execute("PRAGMA user_version")
    user_version = cur.fetchone()[0]
    if user_version == 0:
        _migrate_from_0()


def _migrate_from_0() -> None:
    with open(os.path.join(ROOT_PKG_DIR, "migrate_from_0.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


conn = sqlite3.connect(os.path.join(DATA_DIR, DB_NAME))
cur = conn.cursor()

_init_db()
_update_db()
