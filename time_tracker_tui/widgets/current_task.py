from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

from ..styles import styles


class CurrentTask(Widget, can_focus=False):

    _content: Reactive[str] = Reactive("")
    _placeholder: Reactive[str] = Reactive("Select task")

    def __init__(self, name: str | None = "CurrentTask") -> None:
        super().__init__(name=name)
        self.border_style = styles["INPUT_BORDER_BAD"]
        self.style = styles["INPUT_LOST_FOCUS"]

    def clear_content(self) -> None:
        self._content = ""

    @property
    def content(self) -> str:
        return self._content

    def render(self) -> RenderableType:
        if self._content:
            rendr = Align.center(self._content)
            self.border_style = styles["INPUT_BORDER_GOOD"]
        else:
            rendr = Align.center(self._placeholder)
            self.border_style = styles["INPUT_BORDER_BAD"]

        self.panel = Panel(
            rendr,
            title="Working on",
            border_style=self.border_style,
            height=3,
        )
        return self.panel
