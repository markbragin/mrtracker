from datetime import datetime, timedelta


class Timer():
    def __init__(self) -> None:
        self.restart()
    
    def restart(self):
        self.is_working = False
        self.saved_time = timedelta()

    def switch(self):
        if self.is_working:
            self.is_working = False
            self.saved_time += datetime.now() - self.start_time
        else:
            self.is_working = True
            self.start_time = datetime.now()

    def get_elapsed_time(self):
        if self.is_working:
            self.elapsed_time = datetime.now() - \
                                self.start_time + \
                                self.saved_time
        else:
            self.elapsed_time = self.saved_time
        return self.sec_to_str(self.elapsed_time.seconds)

    @staticmethod
    def sec_to_str(seconds) -> str:
        return f"{seconds // 3600}".zfill(2) + ':' + \
               f"{seconds % 3600 // 60}".zfill(2) + ':' + \
               f"{seconds % 60}".zfill(2)
