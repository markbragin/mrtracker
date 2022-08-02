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
    def elapsed_time(self) -> int:
        if self._on:
            return (datetime.now() - self._start_t).seconds
        else:
            return 0

    @property
    def elapsed_time_str(self) -> str:
        return sec_to_str(self.elapsed_time)

    @property
    def saved_time(self) -> int:
        return self._saved_time.seconds

    @property
    def start_time_str(self) -> str:
        """return start time in %H:%M:%S format"""
        return self._start_t.strftime("%H:%M:%S")

    @property
    def end_time_str(self) -> str:
        """return end time in %H:%M:%S format"""
        return (
            self._start_t + timedelta(seconds=self._saved_time.seconds)
        ).strftime("%H:%M:%S")


def sec_to_str(seconds) -> str:
    if not isinstance(seconds, int):
        return "00:00:00"
    time = f"{seconds % 3600 // 60}:".zfill(3) + f"{seconds % 60}".zfill(2)
    if seconds // 3600:
        time = f"{seconds // 3600}:{time}"
    return time
