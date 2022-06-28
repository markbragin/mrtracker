from __future__ import annotations

from rich.console import RenderableType
from rich.table import Table
from rich.panel import Panel
from textual import events
from textual.reactive import watch

from .. import db
from ..fwidget import Fwidget
from ..styles import styles
from ..stopwatch import Stopwatch as time


class TimeTable(Fwidget):
    def __init__(self, name: str | None = "TimeTable"):
        super().__init__(name=name)
        self.collect_data()

    async def on_mount(self) -> None:
        watch(self.app, "blocked", self.set_can_focus)

    async def set_can_focus(self, blocked: bool) -> None:
        self.can_focus = False if blocked else True

    def on_key(self, event: events.Key) -> None:
        if event.key in ["j", "down"]:
            self._next_item()
        if event.key in ["k", "up"]:
            self._prev_item()

    def _next_item(self) -> None:
        if self.pos < self.len - 1:
            self.pos += 1
            self.refresh()

    def _prev_item(self) -> None:
        if self.pos > 0:
            self.pos -= 1
            self.refresh()
    
    def on_focus(self, event: events.Focus) -> None:
        self.pos = 0
        self.refresh()

    def on_blur(self, event: events.Focus) -> None:
        self.pos = -1
        self.refresh()

    def collect_data(self) -> None:
        self.data = db.fetch_full_info()
        self.pos = -1
        self.len = len(self.data)
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
            title="Time table",
            border_style=styles["TIME_TABLE_BORDER"],
            expand=True,
        )
        return panel
