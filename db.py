import os
from typing import List, Tuple

import sqlite3


conn = sqlite3.connect(os.path.join("db", "time.db"))
cur = conn.cursor()


def _init_db() -> None:
    with open(os.path.join("db", "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def check_db_exists() -> None:
    cur.execute("SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='sessions'")
    table_exists = cur.fetchall()
    if table_exists:
        return
    _init_db()


def _create_total_table() -> None:
    cur.execute("CREATE TABLE tt0 AS "
                "SELECT s.task, sum(s.time) as total "
                "FROM sessions s "
                "GROUP BY s.task")
    conn.commit()


def _create_today_table() -> None:
    cur.execute("CREATE TABLE tt1 AS "
                "SELECT s.task, sum(s.time) as today "
                "FROM sessions s "
                "WHERE s.date = date('now') "
                "GROUP BY s.task")
    conn.commit()


def _create_month_table() -> None:
    cur.execute("CREATE TABLE tt2 AS "
                "SELECT s.task, sum(s.time) as month "
                "FROM sessions s "
                "WHERE s.date LIKE strftime('%Y-%m-%%', 'now') "
                "GROUP BY s.task")
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
    cur.execute("SELECT tt0.task, tt1.today, tt2.month, tt0.total "
                "FROM tt0 "
                "LEFT OUTER JOIN tt1 "
                "ON tt0.task = tt1.task "
                "LEFT OUTER JOIN tt2 "
                "ON tt0.task = tt2.task ")
    result = cur.fetchall()
    _drop_temp_tables()
    return result


check_db_exists()
