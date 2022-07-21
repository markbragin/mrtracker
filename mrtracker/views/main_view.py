from textual.views._grid_view import GridView

from ..widgets.current_task import CurrentTask
from ..widgets.header import MyHeader
from ..widgets.in_app_logger import ialogger
from ..widgets.simple_scrollview import SimpleScrollView
from ..widgets.tasklist import TaskList
from ..widgets.timer import Timer


class MainView(GridView):
    def __init__(self, name: str | None = "MainView") -> None:
        super().__init__(name=name)
        self.header = MyHeader()
        self.current_task = CurrentTask()
        self.timer = Timer()
        self.ialogger = ialogger
        self.tasklist = TaskList()
        self.t_scroll = SimpleScrollView(self.tasklist)

    async def on_mount(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("right", fraction=3)
        self.grid.add_row("header", fraction=1, size=1)
        self.grid.add_row("r1", fraction=1, size=3)
        self.grid.add_row("r2", fraction=1, size=3)
        self.grid.add_row("r3", fraction=1)
        self.grid.add_areas(
            header="left-start|right-end,header",
            current_task="left,r1",
            focus="left,r2",
            logger="left,r3",
            timelist="right,header-end|r3-end",
        )
        self.grid.place(
            header=self.header,
            current_task=self.current_task,
            focus=self.timer,
            logger=self.ialogger,
            timelist=self.t_scroll,
        )
