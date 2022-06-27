CREATE TABLE IF NOT EXISTS sessions(
    id integer NOT NULL primary key,
    task text NOT NULL,
    date text NOT NULL,
    time integer NOT NULL
)
