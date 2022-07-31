from typing import Literal
from rich.table import Table
from rich.panel import Panel
from textual.views._grid_view import GridView

from .. import db
from ..widgets.simple_scrollview import SimpleScrollView
from ..stopwatch import sec_to_str


class StatsView(GridView):
    def __init__(self, name: str | None = "StatsView") -> None:
        super().__init__(name=name)
        self._init_widgets()
        self._make_grid()

    def _init_widgets(self) -> None:
        self.today = SimpleScrollView()
        self.week = SimpleScrollView()
        self.month = SimpleScrollView()

    def _make_grid(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("center", fraction=1)
        self.grid.add_column("right", fraction=1)
        self.grid.add_row("row")

    async def on_mount(self) -> None:
        self._place_widgets()
        await self.update()

    def _place_widgets(self) -> None:
        self.grid.add_areas(
            left="left,row",
            center="center,row",
            right="right,row",
        )
        self.grid.place(
            left=self.today,
            center=self.week,
            right=self.month,
        )

    async def update(self) -> None:
        await self.today.update(self._get_table("today"))
        await self.week.update(self._get_table("week"))
        await self.month.update(self._get_table("month"))

    def _get_table(self, interval: Literal["month", "week", "today"]) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column("Task")
        grid.add_column("Time")
        grid.row_styles = ["white"]
        if interval == "today":
            for row in db.fetch_today():
                grid.add_row(row[0], sec_to_str(row[1]))
            return Panel(grid, title="Today", style="blue")
        elif interval == "week":
            for row in db.fetch_week():
                grid.add_row(row[0], sec_to_str(row[1]))
            return Panel(grid, title="Last 7 days", style="green")
        else:
            for row in db.fetch_month():
                grid.add_row(row[0], sec_to_str(row[1]))
            return Panel(grid, title="Last 30 days", style="red")
