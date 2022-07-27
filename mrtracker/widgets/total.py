from rich.console import RenderableType
from rich.text import Text
from textual.widget import Widget

from ..config import config
from ..stopwatch import sec_to_str
from ..timetuple import TimeTuple
from .entry import Entry, generate_empty_entry


class Total(Widget, can_focus=False):
    def __init__(
        self,
        data: Entry = generate_empty_entry(-1, -1, 'f'),
        name: str | None = "Total",
    ) -> None:
        super().__init__(name=name)
        self._data = data

    def render(self) -> RenderableType:
        time_str = TimeTuple(*map(sec_to_str, self._data.time))
        return Text.assemble(
            f"Today: {time_str.today}   ",
            f"Month: {time_str.month}   ",
            f"Total: {time_str.total}",
            style=config.styles["FOOTER"],
            justify="center",
        )
