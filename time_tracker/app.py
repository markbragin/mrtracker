from datetime import datetime

from textual.app import App
from textual.widgets import Header
from textual.widgets import ScrollView

from . import db
from .widgets.timer import Timer
from .widgets.footer import Footer
from .widgets.input_text import InputText
from .widgets.message import Message
from .widgets.time_table import TimeTable
from .styles import styles


class MyApp(App):

    async def on_load(self) -> None:
        await self.bind("ctrl+c", "quit", "exit")
        await self.bind("ctrl+p", "switch", "pause/resume")
        await self.bind("ctrl+r", "restart", "restart+save")
        await self.bind("ctrl+n", "new_task", "new task")
        await self.bind("enter", "submit", "submit")

    async def on_mount(self) -> None:
        self.header = Header(style=styles["HEADER"])
        self.footer = Footer()
        self.input_text = InputText()
        self.timer = Timer()
        self.message = Message()
        self.table = TimeTable()
        self.scroll = ScrollView(self.table)

        self.grid = await self.view.dock_grid()
        self.grid.add_column("left", fraction=1)
        self.grid.add_column("right", fraction=3)
        self.grid.add_row("header", fraction=1, size=3)
        self.grid.add_row("r1", fraction=1, size=3)
        self.grid.add_row("r2", fraction=1, size=3)
        self.grid.add_row("r3", fraction=1)
        self.grid.add_row("footer", fraction=1, size=1)
        self.grid.add_areas(
            header="left-start|right-end,header",
            input_text="left,r1",
            focus="left,r2",
            message="left,r3",
            table="right,header-end|footer-start",
            footer="left-start|right-end,footer"
        )
        self.grid.place(
            header=self.header,
            input_text=self.input_text,
            focus=self.timer,
            message=self.message,
            table=self.scroll,
            footer=self.footer
        )

    def save_data(self) -> bool:
        if not (self.timer.time and self.input_text.content):
            return False
        db.insert_session(
            self.input_text.content,
            datetime.now().strftime("%Y-%m-%d"),
            self.timer.time
        )
        return True

    async def action_quit(self) -> None:
        self.message.update("Saving data")
        self.save_data()
        self.message.update("Shutdown")
        await self.shutdown()

    async def action_switch(self) -> None:
        if not self.input_text.content:
            self.message.update("Error. Enter the task first", error=True)
            return
        if self.timer.timer.paused:
            self.message.update("Paused")
        else:
            self.message.update("Running")
        self.timer.switch_timer()

    async def action_restart(self) -> None:
        if self.save_data():
            self.table.collect_data()
            await self.scroll.update(self.table)
        self.timer.restart_timer()
        self.message.update("Your data saved. Timer restarted")

    async def action_new_task(self) -> None:
        if self.timer.timer.on:
            self.message.update("Timer is running. "
                                "To start new task restart the timer first.",
                                error=True)
        else:
            await self.input_text.focus()
            self.message.update("Enter the task and press enter")

    async def action_submit(self) -> None:
        if not self.timer.timer.on:
            await self.timer.focus()
            await self.action_switch()
