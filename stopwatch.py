from datetime import datetime, timedelta


class Stopwatch():
    def __init__(self) -> None:
        self.restart()

    def restart(self):
        self.on = False
        self.paused = False
        self.saved_t = timedelta()

    def switch(self):
        self.on = True
        if self.paused:
            self.paused = False
            self.saved_t += datetime.now() - self.start_t
        else:
            self.paused = True
            self.start_t = datetime.now()

    def get_elapsed_time(self):
        if self.paused:
            self.elapsed_t = datetime.now() - self.start_t + self.saved_t
        else:
            self.elapsed_t = self.saved_t
        return self.elapsed_t.seconds

    def get_elapsed_time_str(self):
        return self.sec_to_str(self.get_elapsed_time())

    @staticmethod
    def sec_to_str(seconds) -> str:
        return f"{seconds // 3600}".zfill(2) + ':' + \
               f"{seconds % 3600 // 60}".zfill(2) + ':' + \
               f"{seconds % 60}".zfill(2)
