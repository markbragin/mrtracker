from textual.reactive import Reactive
from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel

from styles import styles


class Message(Widget):

    content: Reactive[str] = Reactive("")
    error: Reactive[bool] = Reactive(False)

    def __init__(self, msg: str = "Welcome to time tracker") -> None:
        super().__init__(name="Message")
        self.content = msg

    def update(self, msg: str, error: bool = False):
        self.error = error
        self.content = msg
        self.refresh()

    def render(self):
        if self.error:
            self.style = styles["MESSAGE_ERROR"]
        else:
            self.style = styles["MESSAGE"]

        self.panel = Panel(
            Align.center(
                self.content,
                vertical="middle",
                style="white"
            ),
            title="Message",
            border_style=self.style,
            expand=True,
        )
        return self.panel
