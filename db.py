import os

import sqlite3


conn = sqlite3.connect(os.path.join("db", "time.db"))
cur = conn.cursor()

table_name = "time_table"


def _init_db():
    with open(os.path.join("db", "createdb.sql"), "r") as file:
        sql = file.read()
    cur.executescript(sql)
    conn.commit()


def check_db_exists():
    cur.execute("SELECT name FROM sqlite_master "
                f"WHERE type='table' AND name='{table_name}'")
    table_exists = cur.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
