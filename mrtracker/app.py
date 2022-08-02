from textual.app import App
from textual.layouts.dock import DockLayout
from textual.reactive import Reactive, events, watch
from textual.view import View
from textual.views._grid_view import GridView

from .config import config
from .views.help_view import HelpView
from .views.main_view import MainView
from .views.stats_view import StatsView
from .widgets.in_app_logger import ialogger


class TimeTracker(App):

    current_view: Reactive[View | None] = Reactive(None)

    async def on_load(self) -> None:
        for action, key in config.app_keys.items():
            await self.bind(key, action)

    async def on_upd(self) -> None:
        await self.stats_v.update()

    async def on_mount(self) -> None:
        self.main_v = MainView()
        self.help_v = HelpView()
        self.stats_v = StatsView()
        self.current_view = self.main_v
        await self.main_v.tasklist.post_message(events.Key(self, "down"))
        await self.main_v.tasklist.post_message(events.Key(self, "down"))
        watch(self, "current_view", self.update_view)

    async def update_view(self, view: GridView) -> None:
        self.clear_screen()
        await self.view.dock(view)
        await view.focus()

    def clear_screen(self) -> None:
        if isinstance(self.view.layout, DockLayout):
            self.view.layout.docks.clear()
        self.view.widgets.clear()

    async def action_quit(self) -> None:
        ialogger.update("[i]Saving data...[/]")
        await self.main_v.save_data()
        await self.shutdown()

    async def action_reset_focus(self) -> None:
        self.current_view = self.main_v

    async def action_save_session(self) -> None:
        await self.main_v.save_data()

    def action_discard_session(self) -> None:
        self.main_v.discard_session()

    async def action_show_help(self) -> None:
        self.current_view = self.help_v

    async def action_show_stats(self) -> None:
        self.current_view = self.stats_v

