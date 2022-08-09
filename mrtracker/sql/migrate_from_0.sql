PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
ALTER TABLE sessions RENAME TO _old_sessions;
CREATE TABLE sessions(
    id INTEGER NOT NULL primary key,
    task_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
	end_time TEXT NOT NULL,
    duration INTEGER as (strftime("%s", end_time) - strftime("%s", start_time)) STORED,
    FOREIGN KEY(task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
INSERT INTO sessions (id, task_id, date, start_time, end_time)
SELECT id, task_id, date, "00:00:00", time(time, "unixepoch")
FROM _old_sessions;
DROP TABLE _old_sessions;
PRAGMA user_version=2;
COMMIT;
