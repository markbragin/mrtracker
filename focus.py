from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel


from timer import Timer
from styles import styles


class Focus(Widget):
    def __init__(self) -> None:
        super().__init__(name="Process")
        self.timer = Timer()

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        self.elapsed_time = self.timer.get_elapsed_time()
        self.content = Panel(
            Align.center(
                self.elapsed_time,
                vertical="middle",
                style=styles["FOCUS"]
            ),
            title="Process",
            border_style=styles["FOCUS_BORDER"],
            expand=True,
        )
        return self.content
