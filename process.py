from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel


from timer import Timer


class Process(Widget):
    def __init__(self, border_style="", style="") -> None:
        super().__init__(name="Process")
        self.timer = Timer()
        self.border_style = border_style
        self.style = style

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        self.elapsed_time = self.timer.get_elapsed_time()
        self.content = Panel(
            Align.center(
                self.elapsed_time,
                vertical="middle",
                style=self.style
            ),
            title="Process",
            border_style=self.border_style,
            expand=True,
        )
        return self.content
