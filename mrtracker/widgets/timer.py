from datetime import datetime, timedelta

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

from ..config import config
from ..stopwatch import Stopwatch, sec_to_str


class Timer(Widget, can_focus=False):

    _working: Reactive[bool] = Reactive(False)

    def __init__(self, name: str | None = "Timer") -> None:
        super().__init__(name=name)
        self.stopwatch = Stopwatch()

    async def on_mount(self):
        self.set_interval(0.5, self.refresh)

    @property
    def elapsed_time(self) -> timedelta:
        return self.stopwatch.elapsed_time

    def get_elapsed_time_str(self) -> str:
        """returns formatted elapsed time [%H:]%M:%S"""
        return sec_to_str(self.stopwatch.elapsed_time.seconds)

    @property
    def saved_time(self) -> timedelta:
        return self.stopwatch.saved_time

    @property
    def start_time(self) -> datetime:
        return self.stopwatch.start_time

    @property
    def end_time(self) -> datetime:
        return self.stopwatch.start_time + timedelta(
            seconds=self.stopwatch.saved_time.seconds
        )

    @property
    def working(self) -> bool:
        return self._working

    def start(self) -> None:
        self.stopwatch.start()

    def stop(self) -> None:
        self.stopwatch.stop()

    def restart(self):
        self.stopwatch.restart()

    def render(self) -> RenderableType:
        self._working = self.stopwatch.on
        self.panel = Panel(
            Align.center(
                self.get_elapsed_time_str(),
                vertical="middle",
                style=config.styles["TIMER_TEXT"],
            ),
            title="for",
            border_style=config.styles["TIMER_BORDER"],
            expand=True,
        )
        return self.panel
