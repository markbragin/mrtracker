from typing import Literal

from rich.panel import Panel
from rich.table import Table
from textual import events
from textual.reactive import Reactive
from textual.views._grid_view import GridView

from .. import db
from ..config import config
from ..stopwatch import sec_to_str
from ..widgets.simple_scrollview import SimpleScrollView


class StatsView(GridView):
    _show_project: Reactive[bool] = Reactive(False)
    _focused: SimpleScrollView | None = None

    def __init__(self, name: str | None = "StatsView") -> None:
        super().__init__(name=name)
        self._init_widgets()
        self._make_grid()
        self.hl = config.styles["STATS_SUBHEADERS_STYLE"]

    def _init_widgets(self) -> None:
        self.today = SimpleScrollView()
        self.week = SimpleScrollView()
        self.month = SimpleScrollView()

    def _make_grid(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("center", fraction=1)
        self.grid.add_column("right", fraction=1)
        self.grid.add_row("row")

    async def on_focus(self) -> None:
        self._focused = self.today
        await self.today.focus()

    async def on_key(self, event: events.Key) -> None:
        if event.key == config.stats_keys["toggle_projects_after_task"]:
            self._show_project = not self._show_project
            await self.update()
        elif event.key in ["left", config.stats_keys["left"]]:
            await self._focus_left()
        elif event.key in ["right", config.stats_keys["right"]]:
            await self._focus_right()
        elif event.key in ["down", config.stats_keys["down"]]:
            if self._focused:
                self._focused.page_down()
        elif event.key in ["up", config.stats_keys["up"]]:
            if self._focused:
                self._focused.page_up()

    async def _focus_left(self) -> None:
        if self._focused is None:
            self._focused = self.month
        elif self._focused == self.month:
            self._focused = self.week
        elif self._focused == self.week:
            self._focused = self.today

    async def _focus_right(self) -> None:
        if self._focused is None:
            self._focused = self.today
        elif self._focused == self.today:
            self._focused = self.week
        elif self._focused == self.week:
            self._focused = self.month

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
        grid.row_styles = [config.styles["STATS_NORMAL_TEXT"]]
        if interval == "today":
            projects = db.fetch_projects_today()
            tasks = db.fetch_tasks_today()
            tags = db.fetch_tags_today()
            title = "Today"
            border_style = config.styles["STATS_TODAY_BORDER_STYLE"]
        elif interval == "week":
            projects = db.fetch_projects_week()
            tasks = db.fetch_tasks_week()
            tags = db.fetch_tags_week()
            title = "Last 7 days"
            border_style = config.styles["STATS_WEEK_BORDER_STYLE"]
        elif interval == "month":
            projects = db.fetch_projects_month()
            tasks = db.fetch_tasks_month()
            tags = db.fetch_tags_month()
            title = "Last 30 days"
            border_style = config.styles["STATS_MONTH_BORDER_STYLE"]
        self._fill_table(grid, projects, tasks, tags)
        return Panel(grid, title=title, border_style=border_style)

    def _fill_table(
        self,
        grid: Table,
        projects: list[tuple],
        tasks: list[tuple],
        tags: list[tuple],
    ) -> None:
        self._insert_projects(grid, projects)
        self._insert_tasks(grid, tasks)
        self._insert_tags(grid, tags)

    def _insert_projects(self, grid: Table, projects: list[tuple]) -> None:
        grid.add_row(f"[{self.hl}]Projects:")
        for row in projects:
            grid.add_row(row[0], sec_to_str(row[1]))
        grid.add_row(end_section=True)

    def _insert_tasks(self, grid: Table, tasks: list[tuple]) -> None:
        grid.add_row(f"[{self.hl}]Tasks:")
        for row in tasks:
            ps = config.styles["STATS_PROJECTS_STYLE"]
            task = (
                f"{row[0]} -> [{ps}]{row[2]}[/]"
                if self._show_project
                else row[0]
            )
            grid.add_row(task, sec_to_str(row[1]))
        grid.add_row(end_section=True)

    def _insert_tags(self, grid: Table, tags: list[tuple]) -> None:
        grid.add_row(f"[{self.hl}]Tags:")
        for row in tags:
            grid.add_row(row[0], sec_to_str(row[1]))
