from datetime import datetime

from textual.reactive import watch
from textual.views._grid_view import GridView

from .. import db
from ..config import config
from ..events import Upd
from ..stopwatch import sec_to_str
from ..widgets.current_task import CurrentTask
from ..widgets.header import MyHeader
from ..widgets.in_app_logger import ialogger
from ..widgets.simple_scrollview import SimpleScrollView
from ..widgets.tasklist import TaskList
from ..widgets.timer import Timer


class MainView(GridView):
    def __init__(self, name: str | None = "MainView") -> None:
        super().__init__(name=name)
        self._init_widgets()
        self._make_grid()

    def _init_widgets(self) -> None:
        self.header = MyHeader()
        self.current_task = CurrentTask()
        self.timer = Timer()
        self.ialogger = ialogger
        self.tasklist = TaskList()
        self.t_scroll = SimpleScrollView(self.tasklist)

    def _make_grid(self) -> None:
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("right", fraction=3)
        self.grid.add_row("header", fraction=1, size=1)
        self.grid.add_row("r1", fraction=1, size=3)
        self.grid.add_row("r2", fraction=1, size=3)
        self.grid.add_row("r3", fraction=1)

    async def on_focus(self) -> None:
        await self.tasklist.focus()

    def on_mount(self) -> None:
        self._place_widgets()
        watch(self.tasklist, "current_task", self.start_task)

    def _place_widgets(self) -> None:
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

    async def start_task(self, current_task) -> None:
        if not current_task:
            self.current_task.clear_content()
        else:
            self.set_current_task(current_task)
            self.switch_timer()

    def set_current_task(self, current_task) -> None:
        self.current_task._content = current_task.title

    def switch_timer(self) -> None:
        if not self.tasklist.current_task:
            ialogger.update("Error. Run the timer first.", error=True)
            return
        if self.timer.timer.paused:
            ialogger.update("Paused")
        else:
            ialogger.update("Running")
        self.timer.switch_timer()

    async def save_session(self) -> None:
        if self.save_data() and self.tasklist.current_task:
            self.tasklist.add_time(self.timer.time)
        hl = config.styles["LOGGER_HIGHLIGHT"]
        ialogger.update(
            "[b]Session saved[/]\n"
            f"[{hl}]{self.current_task.content}[/] - "
            f"{sec_to_str(self.timer.time)}"
        )
        self.tasklist.current_task = None
        self.timer.restart_timer()
        await self.app.post_message_from_child(Upd(self))

    def save_data(self) -> bool:
        if not (self.timer.time and self.tasklist.current_task):
            return False
        db.add_session(
            self.tasklist.current_task.id,
            datetime.now().strftime("%Y-%m-%d"),
            self.timer.time,
        )
        return True

    def discard_session(self) -> None:
        if self.timer._working:
            self.timer.restart_timer()
            self.tasklist.current_task = None
            ialogger.update("Session discarded. Timer reset.")
