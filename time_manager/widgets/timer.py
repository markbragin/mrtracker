from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

from ..config import config
from ..stopwatch import Stopwatch


class Timer(Widget, can_focus=False):

    _working: Reactive[bool] = Reactive(False)

    def __init__(self, name: str | None = "Timer") -> None:
        super().__init__(name=name)
        self.timer = Stopwatch()

    async def on_mount(self):
        self.set_interval(0.5, self.refresh)

    @property
    def time(self) -> int:
        return self.timer.get_elapsed_time()

    @property
    def time_str(self) -> str:
        return self.timer.get_elapsed_time_str()

    def switch_timer(self):
        self.timer.switch()

    def restart_timer(self):
        self.timer.restart()

    def render(self) -> RenderableType:
        self._working = self.timer.on
        self.panel = Panel(
            Align.center(
                self.time_str,
                vertical="middle",
                style=config.styles["TIMER_TEXT"],
            ),
            title="for",
            border_style=config.styles["TIMER_BORDER"],
            expand=True,
        )
        return self.panel