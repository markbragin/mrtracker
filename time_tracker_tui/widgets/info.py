from __future__ import annotations

from textual.reactive import Reactive
from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel
from rich.console import RenderableType

from ..styles import styles


class Info(Widget, can_focus=False):

    _content: Reactive[str] = Reactive("")
    _error: Reactive[bool] = Reactive(False)

    def __init__(self, name: str | None = "Info",
                 msg: str = "Welcome to time tracker.") -> None:
        super().__init__(name=name)
        self._content = msg

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, new_content) -> None:
        self._content = new_content

    @property
    def error(self) -> bool:
        return self._error

    @error.setter
    def error(self, upd) -> None:
        self._error = upd

    def update(self, msg: str, error: bool = False):
        self._error = error
        self._content = msg

    def render(self) -> RenderableType:
        if self._error:
            self.style = styles["INFO_ERROR"]
        else:
            self.style = styles["INFO"]

        self.panel = Panel(
            Align.center(
                self.content,
                vertical="middle",
                style="white"
            ),
            title="Info",
            border_style=self.style,
            expand=True,
        )
        return self.panel
