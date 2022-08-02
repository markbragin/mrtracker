from datetime import timedelta

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

    def get_elapsed_time(self) -> int:
        """returns elapsed time in seconds"""
        return self.stopwatch.elapsed_time.seconds

    def get_elapsed_time_str(self) -> str:
        """returns formatted elapsed time [%H:]%M:%S"""
        return sec_to_str(self.stopwatch.elapsed_time.seconds)

    def get_saved_time(self) -> int:
        """returns saved time in seconds"""
        return self.stopwatch.saved_time.seconds

    def get_start_time(self) -> str:
        """returns formatted start time %H:%M:%S"""
        return self.stopwatch.start_time.strftime("%H:%M:%S")

    def get_end_time(self) -> str:
        """returns formatted end time %H:%M:%S"""
        return (
            self.stopwatch.start_time
            + timedelta(seconds=self.stopwatch.saved_time.seconds)
        ).strftime("%H:%M:%S")

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
