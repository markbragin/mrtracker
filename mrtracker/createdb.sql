CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER NOT NULL primary key,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS links(
    task_id INTEGER NOT NULL primary key,
    parent_id INTEGER NOT NULL,
    FOREIGN KEY(task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY(parent_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK(task_id != parent_id)
);

CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER NOT NULL primary key,
    task_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time INTEGER NOT NULL,
    FOREIGN KEY(task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
);

INSERT INTO tasks VALUES (0, 'root');
INSERT INTO tasks VALUES (1, 'header');
INSERT INTO links VALUES (1, 0);
