from datetime import datetime

from textual.app import App
from textual.layouts.dock import DockLayout
from textual.reactive import Reactive, events, watch
from textual.view import View
from textual.views._grid_view import GridView

from . import db
from .config import config
from .views.help_view import HelpView
from .views.main_view import MainView
from .widgets.in_app_logger import ialogger


class TimeTracker(App):

    current_view: Reactive[View | None] = Reactive(None)

    async def on_load(self) -> None:
        for action, key in config.app_keys.items():
            await self.bind(key, action)

    async def on_mount(self) -> None:
        self.main_v = MainView()
        self.help_v = HelpView()
        self.current_view = self.main_v
        await self.main_v.tasklist.post_message(events.Key(self, "j"))
        await self.main_v.tasklist.post_message(events.Key(self, "j"))
        watch(self, "current_view", self.update_view)
        watch(self.main_v.timer, "_working", self.set_blocked)
        watch(self.main_v.tasklist, "current_task", self.start_task)

    async def update_view(self, view: GridView) -> None:
        self.clear_screen()
        await self.view.dock(view)
        if view is self.main_v:
            await self.action_reset_focus()
        elif view is self.help_v:
            await self.help_v.scrll.focus()

    def clear_screen(self) -> None:
        if isinstance(self.view.layout, DockLayout):
            self.view.layout.docks.clear()
        self.view.widgets.clear()

    async def set_blocked(self, working) -> None:
        self.main_v.tasklist.blocked = working

    async def action_quit(self) -> None:
        ialogger.update("[i]Saving data...[/]")
        self.save_data()
        await self.shutdown()

    def save_data(self) -> bool:
        if not (self.main_v.timer.time and self.main_v.tasklist.current_task):
            return False
        db.add_session(
            self.main_v.tasklist.current_task.task_id,
            datetime.now().strftime("%Y-%m-%d"),
            self.main_v.timer.time,
        )
        return True

    async def action_reset_focus(self) -> None:
        self.current_view = self.main_v
        await self.main_v.tasklist.focus()

    def action_switch_timer(self) -> None:
        if not self.main_v.tasklist.current_task:
            ialogger.update("Error. Run the timer first.", error=True)
            return
        if self.main_v.timer.timer.paused:
            ialogger.update("Paused")
        else:
            ialogger.update("Running")
        self.main_v.timer.switch_timer()

    async def action_save_session(self) -> None:
        if self.save_data() and self.main_v.tasklist.current_task:
            self.main_v.tasklist.add_time(self.main_v.timer.time)
        self.main_v.timer.restart_timer()
        self.main_v.tasklist.current_task = None
        ialogger.update("Your data saved. Timer reset.")

    async def action_show_help(self) -> None:
        self.current_view = self.help_v

    async def start_task(self, current_task) -> None:
        if not current_task:
            self.main_v.current_task.clear_content()
        else:
            self.set_current_task(current_task)
            self.action_switch_timer()

    def set_current_task(self, current_task) -> None:
        if current_task:
            self.main_v.current_task._content = current_task.name
        else:
            self.main_v.current_task.clear_content()
