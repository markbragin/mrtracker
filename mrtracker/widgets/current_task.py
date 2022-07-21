from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

from ..config import config


class CurrentTask(Widget, can_focus=False):

    _content: Reactive[str] = Reactive("")
    _placeholder: Reactive[str] = Reactive("Select task")

    def __init__(self, name: str | None = "CurrentTask") -> None:
        super().__init__(name=name)

    def clear_content(self) -> None:
        self._content = ""

    @property
    def content(self) -> str:
        return self._content

    def render(self) -> RenderableType:
        if self._content:
            rendr = Align.center(self._content)
            border_style = config.styles["CURRENT_TASK_GOOD_BORDER"]
        else:
            rendr = Align.center(self._placeholder)
            border_style = config.styles["CURRENT_TASK_BAD_BORDER"]

        panel = Panel(
            rendr,
            title="Working on",
            style=config.styles["CURRENT_TASK_TEXT"],
            border_style=border_style,
            height=3,
        )
        return panel
