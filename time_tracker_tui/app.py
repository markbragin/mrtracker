from datetime import datetime

from textual.app import App
from textual.reactive import watch, Reactive

from . import db
from .views.main_view import MainView


class MyApp(App):

    blocked: Reactive[bool] = Reactive(False)

    async def on_load(self) -> None:
        await self.bind("ctrl+c", "quit", "exit")
        await self.bind("ctrl+p", "switch", "pause/resume")
        await self.bind("ctrl+r", "restart", "save+reset")
        await self.bind("ctrl+n", "new_task", "new task")
        await self.bind("escape", "reset_focus", "reset focus to the timer")

    async def on_mount(self) -> None:
        self.main_v = MainView()
        await self.view.dock(self.main_v)
        watch(self.main_v.timer, "running", self.set_blocked)

    async def set_blocked(self, running: bool) -> None:
        self.blocked = running

    async def action_quit(self) -> None:
        self.main_v.message.update("Saving data")
        self.save_data()
        self.main_v.message.update("Shutdown")
        await self.shutdown()

    async def action_switch(self) -> None:
        if not self.main_v.input_text.content:
            self.main_v.message.update("Error. Run the timer first",
                                       error=True)
            return
        if self.main_v.timer.timer.paused:
            self.main_v.message.update("Paused")
        else:
            self.main_v.message.update("Running")
        self.main_v.timer.switch_timer()

    async def action_restart(self) -> None:
        if self.save_data():
            self.main_v.table.collect_data()
            await self.main_v.t_scroll.update(self.main_v.table)
        self.main_v.timer.restart_timer()
        self.main_v.input_text.clear_content()
        self.main_v.message.update("Your data saved. Timer reset")

    async def action_new_task(self) -> None:
        if self.main_v.timer.timer.on:
            self.main_v.message.update(
                "Timer is running. "
                "To start new task restart the timer first.",
                error=True,
            )
        else:
            await self.main_v.input_text.focus()
            self.main_v.message.update("Enter the task and press enter")

    async def action_reset_focus(self) -> None:
        await self.set_focus(None)

    async def run_new_task(self) -> None:
        await self.action_reset_focus()
        await self.action_switch()

    def save_data(self) -> bool:
        if not (self.main_v.timer.time and self.main_v.input_text.content):
            return False
        db.insert_session(
            self.main_v.input_text.content,
            datetime.now().strftime("%Y-%m-%d"),
            self.main_v.timer.time,
        )
        return True
