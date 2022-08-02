from datetime import datetime, timedelta


class Stopwatch:

    _on: bool = False
    _start_t: datetime = datetime.now()
    _saved_time = timedelta()

    @property
    def on(self) -> bool:
        return self._on

    def start(self) -> None:
        self._on = True
        self._start_t = datetime.now()

    def stop(self) -> None:
        self._on = False
        self._saved_time = datetime.now() - self._start_t

    def restart(self) -> None:
        self._on = False
        self._saved_time = timedelta()

    @property
    def elapsed_time(self) -> timedelta:
        if self._on:
            return datetime.now() - self._start_t
        else:
            return timedelta()

    @property
    def saved_time(self) -> timedelta:
        return self._saved_time

    @property
    def start_time(self) -> datetime:
        return self._start_t


def sec_to_str(seconds) -> str:
    if not isinstance(seconds, int):
        return "00:00:00"
    time = f"{seconds % 3600 // 60}:".zfill(3) + f"{seconds % 60}".zfill(2)
    if seconds // 3600:
        time = f"{seconds // 3600}:{time}"
    return time
