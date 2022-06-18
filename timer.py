from datetime import datetime, timedelta


class Timer():
    def __init__(self) -> None:
        self.restart()
    
    def restart(self):
        self.on = False
        self.paused = False
        self.saved_time = timedelta()

    def switch(self):
        self.on = True
        if self.paused:
            self.paused = False
            self.saved_time += datetime.now() - self.start_time
        else:
            self.paused = True
            self.start_time = datetime.now()

    def get_elapsed_time(self):
        if self.paused:
            self.elapsed_time = datetime.now() - \
                                self.start_time + \
                                self.saved_time
        else:
            self.elapsed_time = self.saved_time
        return self.elapsed_time.seconds

    def get_elapsed_time_str(self):
        return self.sec_to_str(self.get_elapsed_time())

    @staticmethod
    def sec_to_str(seconds) -> str:
        return f"{seconds // 3600}".zfill(2) + ':' + \
               f"{seconds % 3600 // 60}".zfill(2) + ':' + \
               f"{seconds % 60}".zfill(2)
