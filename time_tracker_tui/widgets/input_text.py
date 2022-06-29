from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.reactive import Reactive
from textual import events
from textual.reactive import watch

from ..fwidget import Fwidget
from ..styles import styles


class InputText(Fwidget):

    _content: Reactive[str] = Reactive("")

    def __init__(self, name: str | None = "InputText") -> None:
        super().__init__(name=name)
        self.border_style = styles["INPUT_BORDER_BAD"]
        self.style = styles["INPUT_LOST_FOCUS"]

    async def on_mount(self) -> None:
        watch(self.app, "blocked_input", self.block)

    async def block(self, blocked_input: bool) -> None:
        self.can_focus = False if blocked_input else True

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, new_content) -> None:
        self._content = new_content

    def clear_content(self) -> None:
        self._content = ""

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+h":
            if self._content:
                self._content = self.content[:-1]
            event.stop()
        elif "ctrl+" in event.key:
            return
        elif event.key == "enter":
            self.app.start_task()
            await self._unfocus()
        elif event.key == "escape":
            self.clear_content()
        else:
            self._content += event.key
            event.stop()

    def on_focus(self, event: events.Focus) -> None:
        self.clear_content()

    def render(self) -> RenderableType:
        if self._has_focus:
            self.style = styles["INPUT_HAS_FOCUS"]
        else:
            self.style = styles["INPUT_LOST_FOCUS"]

        if self._content:
            rendr = Align.center(Text(self.content))
            self.border_style = styles["INPUT_BORDER_GOOD"]
        else:
            rendr = Align.center(Text("Enter your task"))
            self.border_style = styles["INPUT_BORDER_BAD"]

        self.panel = Panel(
            rendr,
            title="Working on",
            border_style=self.border_style,
            height=3,
        )
        return self.panel
