from __future__ import annotations
from webbrowser import Opera

from rich.console import RenderableType
from rich.table import Table
from rich.panel import Panel
from textual import events
from textual.reactive import Reactive

from .. import db
from ..fwidget import Fwidget
from ..styles import styles
from ..stopwatch import Stopwatch as time


class TimeTable(Fwidget):

    _data: Reactive[list[tuple]]
    _pos: Reactive[int] = Reactive(-1)
    _len: Reactive[int] = Reactive(0)

    def __init__(self, name: str | None = "TimeTable"):
        super().__init__(name=name)
        self.collect_data()

    async def on_mount(self) -> None:
        self.watch("_len", self.block)

    async def block(self, length: int) -> None:
        self.can_focus = True if length else False

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def empty(self) -> bool:
        return self._len == 0

    async def on_key(self, event: events.Key) -> None:
        if event.key in ["j", "down"]:
            self._next_item()
        elif event.key in ["k", "up"]:
            self._prev_item()
        elif event.key == "d":
            await self.app.delete_task(self._data[self._pos][0])
            await self._unfocus()
        elif event.key == "enter":
            await self.app.start_existing_task(self._data[self._pos][0])
            await self._unfocus()
        self.refresh()

    def _next_item(self) -> None:
        if self._pos < self._len - 1:
            self._pos += 1

    def _prev_item(self) -> None:
        if self._pos > 0:
            self._pos -= 1

    def on_focus(self, event: events.Focus) -> None:
        self._pos = 0

    def on_blur(self, event: events.Focus) -> None:
        self._pos = -1

    def collect_data(self) -> None:
        self._data = db.fetch_full_info()
        self._pos = -1
        self._len = len(self._data)
        self.refresh()

    def render(self) -> RenderableType:
        table = Table(
            box=None,
            expand=True,
            header_style=styles["TIME_TABLE_HEADER"],
            row_styles=[styles["TIME_TABLE_TEXT"]],
        )

        table.add_column(header="ID", max_width=3)
        table.add_column(header="Task")
        table.add_column(header="Today")
        table.add_column(header="This month")
        table.add_column(header="Total")

        for id, row in enumerate(self._data):
            selected_style = "reverse" if id == self._pos else ""
            table.add_row(
                f"{id + 1}",
                row[0],
                time.sec_to_str(row[1]) if row[1] else time.sec_to_str(0),
                time.sec_to_str(row[2]) if row[2] else time.sec_to_str(0),
                time.sec_to_str(row[3]) if row[3] else time.sec_to_str(0),
                style=selected_style
            )

        panel = Panel(
            table,
            border_style=styles["TIME_TABLE_BORDER"],
            expand=True,
        )
        return panel
