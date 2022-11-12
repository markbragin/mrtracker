from datetime import datetime, timedelta
import os
import sqlite3

from rich import print

from .config import DB_PATH, DB_VERSION, SQL_DIR
from .singleton_meta import SingletonMeta


class Database(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._connect()
        if self._db_exists():
            self._update_db()
        else:
            self._create_db()
        self.cur.execute("PRAGMA foreign_keys=ON")

    def _connect(self) -> None:
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

    def _db_exists(self) -> bool:
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in self.cur.fetchall()}
        return True if tables == {"sessions", "tasks", "projects"} else False

    def _create_db(self) -> None:
        with open(os.path.join(SQL_DIR, "createdb.sql"), "r") as file:
            sql = file.read()
        self.cur.executescript(sql)
        self.conn.commit()

    def _update_db(self) -> None:
        self.cur.execute("PRAGMA user_version")
        user_version = self.cur.fetchone()[0]
        if user_version < DB_VERSION:
            try:
                self._migrate(user_version)
            except FileNotFoundError:
                print(
                    "[red]Whoops. Seems like wrong db version.[/]\n"
                    "[green]Contact developer.\n[/]"
                    "[blue]https://github.com/markbragin/mrtracker"
                )
                exit(2)

    def _migrate(self, old_version: int) -> None:
        sql_script = f"migrate_from_{old_version}.sql"
        with open(os.path.join(SQL_DIR, sql_script), "r") as file:
            sql = file.read()
        self.cur.executescript(sql)
        self.conn.commit()

    def fetch_tasks(self) -> list[tuple]:
        self.cur.execute(
            "SELECT t.id, p.id, t.name, SUM(s.duration), t.tags "
            "FROM tasks t "
            "LEFT JOIN projects p "
            "ON t.project_id = p.id "
            "LEFT JOIN sessions s "
            "ON t.id = s.task_id "
            "GROUP BY t.id "
            "ORDER BY t.id"
        )
        return self.cur.fetchall()

    def fetch_projects(self) -> list[tuple]:
        self.cur.execute(
            "SELECT id, NULL, name, NULL, NULL FROM projects p ORDER BY p.id"
        )
        return self.cur.fetchall()

    def fetch_tasks_today(self) -> list[tuple]:
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_tasks_week(self) -> list[tuple]:
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_tasks_month(self) -> list[tuple]:
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_projects_today(self) -> list[tuple]:
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_projects_week(self) -> list[tuple]:
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_projects_month(self) -> list[tuple]:
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        self.cur.execute(
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
        return self.cur.fetchall()

    def fetch_tags_today(self) -> list[tuple]:
        self.cur.execute(
            "SELECT t.tags, SUM(s.duration) sum "
            "FROM sessions s "
            "LEFT JOIN tasks t "
            "ON t.id = s.task_id "
            "WHERE t.tags IS NOT NULL AND date = date('now', 'localtime') "
            "GROUP BY t.tags "
            "ORDER BY sum DESC"
        )
        return self.cur.fetchall()

    def fetch_tags_week(self) -> list[tuple]:
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        self.cur.execute(
            "SELECT t.tags, SUM(s.duration) sum "
            "FROM sessions s "
            "LEFT JOIN tasks t "
            "ON t.id = s.task_id "
            "WHERE t.tags IS NOT NULL AND date BETWEEN (?) AND (?) "
            "GROUP BY t.tags "
            "ORDER BY sum DESC",
            (week_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
        )
        return self.cur.fetchall()

    def fetch_tags_month(self) -> list[tuple]:
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        self.cur.execute(
            "SELECT t.tags, SUM(s.duration) sum "
            "FROM sessions s "
            "LEFT JOIN tasks t "
            "ON t.id = s.task_id "
            "WHERE t.tags IS NOT NULL AND date BETWEEN (?) AND (?) "
            "GROUP BY t.tags "
            "ORDER BY sum DESC",
            (month_ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")),
        )
        return self.cur.fetchall()

    def fetch_for_csv(self) -> list[tuple]:
        """fetches project|task|tags|date|start_time|end_time|duration(str)"""
        self.cur.execute(
            "SELECT p.name, t.name, t.tags, s.date, "
            "s.start_time, s.end_time, time(s.duration, 'unixepoch') "
            "FROM sessions s "
            "LEFT JOIN tasks t "
            "ON s.task_id = t.id "
            "LEFT JOIN projects p "
            "ON t.project_id = p.id "
        )
        return self.cur.fetchall()

    def add_session(
        self,
        task_id: int,
        date: str,
        start_time: str,
        end_time: str,
    ) -> None:
        self.cur.execute(
            "INSERT INTO sessions (task_id, date, start_time, end_time) "
            "VALUES (?, ?, ?, ?)",
            (task_id, date, start_time, end_time),
        )
        self.conn.commit()

    def add_project(self, name: str) -> None:
        self.cur.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        self.conn.commit()

    def add_task(self, name: str, project_id: int) -> None:
        self.cur.execute(
            "INSERT INTO tasks (name, project_id) VALUES (?, ?)",
            (name, project_id),
        )
        self.conn.commit()

    def delete_project(self, project_id: int) -> None:
        self.cur.execute("DELETE FROM projects WHERE id=(?)", (project_id,))
        self.conn.commit()

    def delete_task(self, task_id: int) -> None:
        self.cur.execute("DELETE FROM tasks WHERE id=(?)", (task_id,))
        self.conn.commit()

    def rename_project(self, project_id: int, new_name: str) -> None:
        self.cur.execute(
            "UPDATE projects SET name = (?) WHERE id=(?)",
            (new_name, project_id),
        )
        self.conn.commit()

    def rename_task(self, task_id: int, new_name: str) -> None:
        self.cur.execute(
            "UPDATE tasks SET name = (?) WHERE id=(?)",
            (new_name, task_id),
        )
        self.conn.commit()

    def update_tags(self, task_ids: list[int], tag: str | None) -> None:
        placeholders = ", ".join("?" for _ in task_ids)
        self.cur.execute(
            "UPDATE tasks SET tags=(?) WHERE id in (%s)" % placeholders,
            (tag, *task_ids),
        )
        self.conn.commit()

    def change_project(self, task_id: int, new_project_id: int) -> None:
        self.cur.execute(
            "UPDATE tasks SET project_id = (?) WHERE id=(?)",
            (new_project_id, task_id),
        )
        self.conn.commit()

    def swap_projects(self, id1: int, id2: int) -> None:
        self.cur.execute("UPDATE projects SET id=-1 WHERE id=(?)", (id1,))
        self.cur.execute("UPDATE projects SET id=(?) WHERE id=(?)", (id1, id2))
        self.cur.execute("UPDATE projects SET id=(?) WHERE id=-1", (id2,))
        self.conn.commit()

    def swap_tasks(self, id1: int, id2: int) -> None:
        self.cur.execute("UPDATE tasks SET id=-1 WHERE id=(?)", (id1,))
        self.cur.execute("UPDATE tasks SET id=(?) WHERE id=(?)", (id1, id2))
        self.cur.execute("UPDATE tasks SET id=(?) WHERE id=-1", (id2,))
        self.conn.commit()

    def delete_sessions_by_task_ids(self, task_ids: list[int]) -> None:
        placeholders = ", ".join("?" for _ in task_ids)
        self.cur.execute(
            "DELETE FROM sessions WHERE task_id in (%s)" % placeholders,
            task_ids,
        )
        self.conn.commit()

    def get_next_task_id(self) -> int:
        self.cur.execute("SELECT MAX(id) FROM tasks")
        id = self.cur.fetchone()[0]
        return id + 1 if id else 1

    def get_next_project_id(self) -> int:
        self.cur.execute("SELECT MAX(id) FROM projects")
        id = self.cur.fetchone()[0]
        return id + 1 if id else 1
