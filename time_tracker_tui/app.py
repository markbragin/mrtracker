from datetime import datetime

from textual.app import App
from textual.reactive import watch, Reactive

from . import db
from .views.main_view import MainView
from .operation import Operation


class MyApp(App):

    blocked_input: Reactive[bool] = Reactive(False)
    operation: Reactive[Operation] = Reactive(Operation.none)

    async def on_load(self) -> None:
        await self.bind("ctrl+c", "quit", "exit")
        await self.bind("t", "focus_table", "switch focus to the table")
        await self.bind("escape", "reset_focus", "reset focus to the timer")
        await self.bind("ctrl+p", "switch", "pause/resume")
        await self.bind("ctrl+r", "restart", "save+reset")
        await self.bind("ctrl+n", "new_task", "new task")

    async def on_mount(self) -> None:
        self.main_v = MainView()
        await self.view.dock(self.main_v)
        watch(self.main_v.timer, "_working", self.set_blocked)

    async def set_blocked(self, running: bool) -> None:
        self.blocked_input = running

    async def action_quit(self) -> None:
        self.main_v.info.update("[i]Saving data...[/]")
        self.save_data()
        self.main_v.info.update("Shutdown")
        await self.shutdown()

    def save_data(self) -> bool:
        if not (self.main_v.timer.time and self.main_v.input_text.content):
            return False
        db.insert_session(
            self.main_v.input_text.content,
            datetime.now().strftime("%Y-%m-%d"),
            self.main_v.timer.time,
        )
        return True

    async def action_focus_table(self) -> None:
        await self.main_v.table.focus()

    async def action_reset_focus(self) -> None:
        await self.set_focus(None)

    def action_switch(self) -> None:
        if not self.main_v.input_text.content:
            self.main_v.info.update("Error. Run the timer first.",
                                    error=True)
            return
        if self.main_v.timer.timer.paused:
            self.main_v.info.update("Paused")
        else:
            self.main_v.info.update("Running")
        self.main_v.timer.switch_timer()

    async def action_restart(self) -> None:
        if self.save_data():
            self.main_v.table.collect_data()
            await self.main_v.t_scroll.update(self.main_v.table)
        self.main_v.timer.restart_timer()
        self.main_v.input_text.clear_content()
        self.main_v.info.update("Your data saved. Timer reset.")

    async def action_new_task(self) -> None:
        if self.blocked_input:
            self.main_v.info.update(
                "[b]Timer is running[/]. "
                "To start new task restart the timer first.",
                error=True,
            )
        else:
            await self.main_v.input_text.focus()
            self.main_v.info.update("Enter the task and press [b]ENTER[/].")

    async def delete_task(self, task: str) -> None:
        db.delete_task(task)
        self.main_v.table.collect_data()
        await self.main_v.t_scroll.update(self.main_v.table)
        self.main_v.info.update(f"[b green]{task}[/] has been deleted.")

    async def start_existing_task(self, task: str) -> None:
        if self.main_v.timer._working:
            self.main_v.info.update(
                "[b]Timer is running[/]. "
                "To start new task restart the timer first.",
                error=True,
            )
        else:
            self.main_v.input_text.content = task
            self.start_task()

    def start_task(self) -> None:
        self.action_switch()
