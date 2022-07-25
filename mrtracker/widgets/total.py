from rich.console import RenderableType
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from ..stopwatch import sec_to_str
from .entry import Entry, generate_empty_entry


class Total(Widget, can_focus=False):

    _data: Reactive[Entry]

    def __init__(
        self,
        data: Entry = generate_empty_entry(-1, -1),
        name: str | None = "Total",
    ) -> None:
        super().__init__(name=name)
        self._data = data

    def render(self) -> RenderableType:
        return Text(
            f"Today: {sec_to_str(self._data.today)} "
            + f"Month: {sec_to_str(self._data.month)} "
            + f"Total: {sec_to_str(self._data.total)} ",
            style="on black",
        )
