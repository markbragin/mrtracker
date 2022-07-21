from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

from ..__init__ import __version__
from ..config import config


class Logger(Widget, can_focus=False):

    _content: Reactive[str] = Reactive("")
    _error: Reactive[bool] = Reactive(False)

    def __init__(
        self,
        name: str | None = "Logger",
    ) -> None:
        super().__init__(name=name)
        self._content = (
            f"MRTracker v{__version__}\n"
            + f"[{config.styles['LOGGER_HIGHLIGHT']}]"
            + f"{config.app_keys['show_help']}[/] - show help"
        )

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
            border_style = config.styles["LOGGER_ERROR_BORDER"]
        else:
            border_style = config.styles["LOGGER_BORDER"]

        self.panel = Panel(
            Align.center(self.content, vertical="middle", style="white"),
            border_style=border_style,
            expand=True,
        )
        return self.panel


ialogger = Logger()
