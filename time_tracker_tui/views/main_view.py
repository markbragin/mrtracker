from __future__ import annotations

from textual.views._grid_view import GridView
from textual.widgets import ScrollView
from textual.widgets import Header

from ..widgets.input_text import InputText
from ..widgets.timer import Timer
from ..widgets.time_table import TimeTable
from ..widgets.info import Info
from ..styles import styles


class MainView(GridView):
    def __init__(self, name: str | None = "MainView") -> None:
        super().__init__(name=name)
        self.header = Header(style=styles["HEADER"])
        self.input_text = InputText()
        self.timer = Timer()
        self.info = Info()
        self.table = TimeTable()
        self.t_scroll = ScrollView(self.table)

    async def on_mount(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("right", fraction=3)
        self.grid.add_row("header", fraction=1, size=3)
        self.grid.add_row("r1", fraction=1, size=3)
        self.grid.add_row("r2", fraction=1, size=3)
        self.grid.add_row("r3", fraction=1)
        self.grid.add_areas(
            header="left-start|right-end,header",
            input_text="left,r1",
            focus="left,r2",
            info="left,r3",
            table="right,header-end|r3-end",
        )
        self.grid.place(
            header=self.header,
            input_text=self.input_text,
            focus=self.timer,
            info=self.info,
            table=self.t_scroll,
        )
