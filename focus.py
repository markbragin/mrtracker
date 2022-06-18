from datetime import datetime

from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel

import db
from timer import Timer
from styles import styles


class Focus(Widget):
    def __init__(self) -> None:
        super().__init__(name="Focus")
        self.task_name = ""
        self.timer = Timer()

    async def on_mount(self):
        await self.focus()
        self.set_interval(0.5, self.refresh)

    def switch_timer(self):
        self.timer.switch()

    def restart_timer(self):
        self.timer.restart()

    def save_data(self):
        time = self.timer.get_elapsed_time()
        if not self.task_name and not time:
            return

        date = datetime.now().strftime("%Y-%m-%d")
        db.insert_session(self.task_name.lower(), date, time)

    def render(self):
        self.elapsed_time = self.timer.get_elapsed_time_str()
        self.panel = Panel(
            Align.center(
                self.elapsed_time,
                vertical="middle",
                style=styles["FOCUS"]
            ),
            title="Focus time",
            border_style=styles["FOCUS_BORDER"],
            expand=True,
        )
        return self.panel
