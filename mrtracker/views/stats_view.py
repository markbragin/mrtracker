from typing import Literal

from rich.panel import Panel
from rich.table import Table
from textual import events
from textual.views._grid_view import GridView

from ..db import Database
from ..config import config
from ..stopwatch import sec_to_str
from ..widgets.simple_scrollview import SimpleScrollView


TimeInterval = Literal["today", "week", "month"]

SSS = config.styles["STATS_SUBHEADERS_STYLE"]
SPS = config.styles["STATS_PROJECTS_STYLE"]

db = Database()


class StatsView(GridView):
    _show_project: bool = False
    _focused: SimpleScrollView | None = None
    _need_update: bool = False

    today: SimpleScrollView
    week: SimpleScrollView
    month: SimpleScrollView

    projects: dict[TimeInterval, list[tuple]] = dict()
    tasks: dict[TimeInterval, list[tuple]] = dict()
    tags: dict[TimeInterval, list[tuple]] = dict()

    def __init__(self, name: str | None = "StatsView") -> None:
        super().__init__(name=name)
        self._make_view_grid()
        self._collect_data()
        self._init_widgets()

    def _make_view_grid(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("center", fraction=1)
        self.grid.add_column("right", fraction=1)
        self.grid.add_row("row")

    def _collect_data(self) -> None:
        self.projects["today"] = db.fetch_projects_today()
        self.projects["week"] = db.fetch_projects_week()
        self.projects["month"] = db.fetch_projects_month()
        self.tasks["today"] = db.fetch_tasks_today()
        self.tasks["week"] = db.fetch_tasks_week()
        self.tasks["month"] = db.fetch_tasks_month()
        self.tags["today"] = db.fetch_tags_today()
        self.tags["week"] = db.fetch_tags_week()
        self.tags["month"] = db.fetch_tags_month()

    def _init_widgets(self) -> None:
        self.today = SimpleScrollView(self._get_today_section())
        self.week = SimpleScrollView(self._get_week_section())
        self.month = SimpleScrollView(self._get_month_section())

    def _get_today_section(self) -> Panel:
        grid = self._get_section_grid()
        self._fill_grid(grid, "today")
        return Panel(
            grid,
            title="Today",
            border_style=config.styles["STATS_TODAY_BORDER_STYLE"],
        )

    def _get_week_section(self) -> Panel:
        grid = self._get_section_grid()
        self._fill_grid(grid, "week")
        return Panel(
            grid,
            title="Last 7 days",
            border_style=config.styles["STATS_WEEK_BORDER_STYLE"],
        )

    def _get_month_section(self) -> Panel:
        grid = self._get_section_grid()
        self._fill_grid(grid, "month")
        return Panel(
            grid,
            title="Last 30 days",
            border_style=config.styles["STATS_MONTH_BORDER_STYLE"],
        )

    def _get_section_grid(self) -> Table:
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column("Task", justify="left", overflow="fold")
        grid.add_column("Time", justify="right", no_wrap=True)
        grid.row_styles = [config.styles["STATS_NORMAL_TEXT"]]
        return grid

    def _fill_grid(self, grid: Table, ti: TimeInterval) -> None:
        self._insert_projects(grid, ti)
        self._insert_tasks(grid, ti)
        self._insert_tags(grid, ti)

    def _insert_projects(self, grid: Table, ti: TimeInterval) -> None:
        grid.add_row(f"[{SSS}]Projects:")
        for row in self.projects[ti]:
            grid.add_row(row[0], sec_to_str(row[1]))
        grid.add_row(end_section=True)

    def _insert_tasks(self, grid: Table, ti: TimeInterval) -> None:
        grid.add_row(f"[{SSS}]Tasks:")
        for row in self.tasks[ti]:
            task = (
                f"{row[0]} -> [{SPS}]{row[2]}[/]"
                if self._show_project
                else row[0]
            )
            grid.add_row(task, sec_to_str(row[1]))
        grid.add_row(end_section=True)

    def _insert_tags(self, grid: Table, ti: TimeInterval) -> None:
        grid.add_row(f"[{SSS}]Tags:")
        for row in self.tags[ti]:
            grid.add_row(row[0], sec_to_str(row[1]))

    async def on_mount(self) -> None:
        self._place_widgets()

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

    async def _update(self) -> None:
        self._collect_data()
        await self._rerender()

    async def _rerender(self) -> None:
        await self.today.update(self._get_today_section())
        await self.week.update(self._get_week_section())
        await self.month.update(self._get_month_section())

    async def on_focus(self) -> None:
        if not self._focused:
            self._focused = self.today
        await self._focused.focus()
        if self._need_update:
            await self._update()
            self._need_update = False

    async def on_key(self, event: events.Key) -> None:
        if event.key == config.stats_keys["toggle_projects_after_task"]:
            self._show_project = not self._show_project
            await self._update()
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

    def require_update(self) -> None:
        self._need_update = True
