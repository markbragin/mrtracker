from datetime import datetime

from textual.reactive import watch
from textual.views._grid_view import GridView

from .. import db
from ..config import config
from ..events import DbUpdate
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
        self.grid.add_column("right", min_size=50, fraction=3)
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
            self.start_session()

    def set_current_task(self, current_task) -> None:
        self.current_task._content = current_task.title

    def start_session(self) -> None:
        self.timer.start()

    async def save_data(self) -> None:
        self.timer.stop()
        if self.timer.saved_time.seconds and self.tasklist.current_task:
            if self.timer.end_time.date() > self.timer.start_time.date():
                self._split_session_and_save()
            else:
                self._save_session()
            await self.app.post_message_from_child(DbUpdate(self))
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                "[b]Session saved[/]\n"
                f"[{hl}]{self.current_task.content}[/] - "
                f"{sec_to_str(self.timer.saved_time.seconds)}"
            )
        self.tasklist.current_task = None
        self.timer.restart()

    def _split_session_and_save(self) -> None:
        end_of_first_day = self.timer.start_time.replace(
            hour=23, minute=59, second=59
        )
        duration1 = (end_of_first_day - self.timer.start_time).seconds + 1
        db.add_session(
            self.tasklist.current_task.id,
            self.timer.start_time.strftime("%Y-%m-%d"),
            self.timer.start_time.strftime("%H:%M:%S"),
            end_of_first_day.strftime("%H:%M:%S"),
            duration1,
        )
        self.tasklist.add_time(duration1)

        start_of_second_day = self.timer.end_time.replace(
            hour=0, minute=0, second=0
        )
        duration2 = (self.timer.end_time - start_of_second_day).seconds
        db.add_session(
            self.tasklist.current_task.id,
            self.timer.end_time.strftime("%Y-%m-%d"),
            start_of_second_day.strftime("%H:%M:%S"),
            self.timer.end_time.strftime("%H:%M:%S"),
            duration2,
        )
        self.tasklist.add_time(duration2)

    def _save_session(self) -> None:
        db.add_session(
            self.tasklist.current_task.id,
            self.timer.start_time.strftime("%Y-%m-%d"),
            self.timer.start_time.strftime("%H:%M:%S"),
            self.timer.end_time.strftime("%H:%M:%S"),
            self.timer.saved_time.seconds,
        )
        self.tasklist.add_time(self.timer.saved_time.seconds)

    def discard_session(self) -> None:
        if self.timer._working:
            self.timer.restart()
            self.tasklist.current_task = None
            ialogger.update("Session discarded. Timer reset.")
