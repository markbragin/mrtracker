PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS projects(
	id INTEGER NOT NULL PRIMARY KEY,
	name INTEGER NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER NOT NULL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    tags TEXT,
    FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER NOT NULL primary key,
    task_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY(task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
COMMIT;
