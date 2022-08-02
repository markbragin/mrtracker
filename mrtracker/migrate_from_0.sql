PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE temp_sessions AS select * from sessions;
DROP TABLE sessions;
CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER NOT NULL primary key,
    task_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
	end_time TEXT NOT NULL,
	duration INTEGER NOT NULL,
    FOREIGN KEY(task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
INSERT INTO sessions (id, task_id, date, start_time, end_time, duration)
SELECT id, task_id, date, "00:00:00", time(time, "unixepoch"), time
FROM temp_sessions;
PRAGMA user_version=1;
COMMIT;
