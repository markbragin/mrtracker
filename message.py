from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel

from timer import Timer
from styles import styles


class Message(Widget):
    def __init__(self, msg="Welcome to time_tracker TUI") -> None:
        super().__init__(name="Message")
        self.content = msg
        self._style = styles["MESSAGE"]
        self.error = False

    def update(self, msg: str, error: bool = False):
        self.error = error
        self.content = msg
        self.refresh()

    def render(self):
        if self.error:
            self._style = styles["MESSAGE_ERROR"]
        else:
            self._style = styles["MESSAGE"]

        self.panel = Panel(
            Align.center(
                self.content,
                vertical="middle",
                style="white"
            ),
            title="Message",
            border_style=self._style,
            expand=True,
        )
        return self.panel

