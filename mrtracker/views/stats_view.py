from typing import Literal

from rich.panel import Panel
from rich.table import Table
from textual.views._grid_view import GridView

from .. import db
from ..stopwatch import sec_to_str
from ..widgets.simple_scrollview import SimpleScrollView


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
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column("Task", justify="left", overflow="fold")
        grid.add_column("Time", justify="right", no_wrap=True)
        grid.row_styles = ["white"]
        if interval == "today":
            projects = db.fetch_projects_today()
            tasks = db.fetch_tasks_today()
            tags = db.fetch_tags_today()
            title = "Today"
            style = "blue"
        elif interval == "week":
            projects = db.fetch_projects_week()
            tasks = db.fetch_tasks_week()
            tags = db.fetch_tags_week()
            title = "Last 7 days"
            style = "green"
        elif interval == "month":
            projects = db.fetch_projects_month()
            tasks = db.fetch_tasks_month()
            tags = db.fetch_tags_month()
            title = "Last 30 days"
            style = "red"

        grid.add_row("[magenta]Projects:")
        for row in projects:
            grid.add_row(row[0], sec_to_str(row[1]))
        grid.add_row(end_section=True)

        grid.add_row("[magenta]Tasks:")
        for row in tasks:
            grid.add_row(row[0], sec_to_str(row[1]))
        grid.add_row(end_section=True)

        grid.add_row("[magenta]Tags:")
        for row in tags:
            grid.add_row(row[0], sec_to_str(row[1]))

        return Panel(grid, title=title, style=style)
