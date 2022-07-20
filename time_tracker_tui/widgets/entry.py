from enum import Enum, auto

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.reactive import Reactive, events

from ..mode import Mode
from ..stopwatch import sec_to_str
from .text_input import TextInput


class EntryType(Enum):
    FOLDER = auto()
    TASK = auto()


class Entry(TextInput):

    task_id: Reactive[int]
    parent_id: Reactive[int]
    name: Reactive[str]
    today: Reactive[int]
    month: Reactive[int]
    total: Reactive[int]

    def __init__(self, data: tuple, name: str = "Entry") -> None:
        super().__init__(name=name)
        self.task_id = data[0]
        self.parent_id = data[1]
        self.name = data[2]
        self.today = data[3]
        self.month = data[4]
        self.total = data[5]

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.content:
            self.name = self.content
        else:
            super().on_key(event)

    @property
    def type(self) -> EntryType:
        return EntryType.FOLDER if self.parent_id == 0 else EntryType.TASK

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
        return Text(
            (
                sec_to_str(self.today).ljust(12, " ")
                + sec_to_str(self.month).ljust(12, " ")
                + sec_to_str(self.total).ljust(12, " ")
            ),
            justify="right",
        )

    def _render_name(
        self, mode: Mode = Mode.NORMAL, expanded: bool = False
    ) -> RenderableType:
        name = self._render_with_cursor() if mode == Mode.INSERT else self.name
        if self.type is EntryType.FOLDER:
            name = f"🗁  {name}" if expanded else f"🗀 {name}"
        return name


def generate_empty_entry(task_id: int, parent_id: int) -> Entry:
    return Entry((task_id, parent_id, "", 0, 0, 0))