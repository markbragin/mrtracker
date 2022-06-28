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
from ..operation import Operation


class TimeTable(Fwidget):

    data: Reactive[list[tuple]]
    pos: Reactive[int]

    def __init__(self, name: str | None = "TimeTable"):
        super().__init__(name=name)
        self.collect_data()

    async def on_key(self, event: events.Key) -> None:
        if event.key in ["j", "down"]:
            self._next_item()
        elif event.key in ["k", "up"]:
            self._prev_item()
        elif event.key == "enter":
            if self.app.operation == Operation.delete:
                await self.app.delete_task(self.data[self.pos][0])
            elif self.app.operation == Operation.start:
                await self.app.start_existing_task(self.data[self.pos][0])
            await self._unfocus()
        self.refresh()

    def _next_item(self) -> None:
        if self.pos < self.len - 1:
            self.pos += 1

    def _prev_item(self) -> None:
        if self.pos > 0:
            self.pos -= 1

    def on_focus(self, event: events.Focus) -> None:
        self.pos = 0

    def on_blur(self, event: events.Focus) -> None:
        self.pos = -1

    def collect_data(self) -> None:
        self.data = db.fetch_full_info()
        self.pos = -1
        self.len = len(self.data)
        self.refresh()

    @property
    def empty(self) -> bool:
        return self.len == 0

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

        for id, row in enumerate(self.data):
            selected_style = "reverse" if id == self.pos else ""
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
