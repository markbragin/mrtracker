from __future__ import annotations

from textual.views._grid_view import GridView
from textual.widgets import ScrollView
from textual.widgets import Header

from ..widgets.footer import Footer
from ..widgets.input_text import InputText
from ..widgets.timer import Timer
from ..widgets.time_table import TimeTable
from ..widgets.message import Message
from ..styles import styles


class MainView(GridView):
    def __init__(self, name: str | None = "MainView") -> None:
        super().__init__(name=name)
        self.header = Header(style=styles["HEADER"])
        self.footer = Footer()
        self.input_text = InputText()
        self.timer = Timer()
        self.message = Message()
        self.table = TimeTable()
        self.t_scroll = ScrollView(self.table)

    async def on_mount(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("right", fraction=3)
        self.grid.add_row("header", fraction=1, size=3)
        self.grid.add_row("r1", fraction=1, size=3)
        self.grid.add_row("r2", fraction=1, size=3)
        self.grid.add_row("r3", fraction=1)
        self.grid.add_row("footer", fraction=1, size=1)
        self.grid.add_areas(
            header="left-start|right-end,header",
            input_text="left,r1",
            focus="left,r2",
            message="left,r3",
            table="right,header-end|footer-start",
            footer="left-start|right-end,footer",
        )
        self.grid.place(
            header=self.header,
            input_text=self.input_text,
            focus=self.timer,
            message=self.message,
            table=self.t_scroll,
            footer=self.footer,
        )
