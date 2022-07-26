from enum import Enum, auto

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.reactive import Reactive, events

from ..mode import Mode
from ..stopwatch import sec_to_str
from ..timetuple import TimeTuple
from .text_input import TextInput


class EntryType(Enum):
    FOLDER = auto()
    TASK = auto()


class Entry(TextInput):

    task_id: int
    parent_id: int
    name: str
    own_time: TimeTuple
    time: TimeTuple

    def __init__(self, data: tuple, name: str = "Entry") -> None:
        super().__init__(name=name)
        self.task_id = data[0]
        self.parent_id = data[1]
        self.name = data[2]
        self.own_time = TimeTuple(
            data[3] if data[3] else 0,
            data[4] if data[4] else 0,
            data[5] if data[5] else 0,
        )
        self.time = self.own_time

    def on_key(self, event: events.Key) -> None:
        super().on_key(event)

    @property
    def type(self) -> EntryType:
        return EntryType.FOLDER if self.parent_id == 0 else EntryType.TASK

    def reset_own_time(self) -> None:
        self.own_time = TimeTuple(0, 0, 0)

    def render(
        self, mode: Mode = Mode.NORMAL, expanded: bool = False
    ) -> RenderableType:
        grid = Table.grid(expand=True)
        grid.add_row(
            self._render_name(mode=mode, expanded=expanded),
            self._render_time(),
        )
        return grid

    def _render_time(self) -> RenderableType:
        time_str = map(sec_to_str, self.time)
        return Text.assemble(
            *map(lambda x: x.ljust(12, " "), time_str),
            justify="right",
        )

    def _render_name(
        self, mode: Mode = Mode.NORMAL, expanded: bool = False
    ) -> RenderableType:
        name = self._render_with_cursor() if mode != Mode.NORMAL else self.name
        if self.type is EntryType.FOLDER:
            name = f"🗁  {name}" if expanded else f"🗀 {name}"
        return name


def generate_empty_entry(task_id: int, parent_id: int) -> Entry:
    return Entry((task_id, parent_id, "", 0, 0, 0))
