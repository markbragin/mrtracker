from datetime import datetime, timedelta


class Stopwatch():

    _on: bool = False
    _paused: bool = False

    def __init__(self) -> None:
        self.restart()

    @property
    def on(self) -> bool:
        return self._on

    @property
    def paused(self) -> bool:
        return self._paused

    def restart(self):
        self._on = False
        self._paused = False
        self._saved_t = timedelta()

    def switch(self):
        self._on = True
        if self._paused:
            self._paused = False
            self._saved_t += datetime.now() - self._start_t
        else:
            self._paused = True
            self._start_t = datetime.now()

    def get_elapsed_time(self):
        if self._paused:
            self._elapsed_t = datetime.now() - self._start_t + self._saved_t
        else:
            self._elapsed_t = self._saved_t
        return self._elapsed_t.seconds

    def get_elapsed_time_str(self):
        return self.sec_to_str(self.get_elapsed_time())

    @staticmethod
    def sec_to_str(seconds) -> str:
        return f"{seconds // 3600}".zfill(2) + ':' + \
               f"{seconds % 3600 // 60}".zfill(2) + ':' + \
               f"{seconds % 60}".zfill(2)
