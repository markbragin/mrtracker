from enum import Enum, auto

from textual.app import App
from textual.widgets import Header
from textual.widgets import ScrollView


from focus import Focus
from footer import Footer
from input import Input
from message import Message
from time_table import TimeTable
from styles import styles


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
        self.input = Input()
        self.focus = Focus()
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
            input="left,r1",
            focus="left,r2",
            message="left,r3",
            table="right,header-end|footer-start",
            footer="left-start|right-end,footer"
        )
        self.grid.place(
            header=self.header,
            input=self.input,
            focus=self.focus,
            message=self.message,
            table=self.scroll,
            footer=self.footer
        )

    async def action_quit(self):
        self.message.update("Saving data")
        self.focus.save_data()
        self.message.update("Shutdown")
        await self.shutdown()

    async def action_switch(self):
        if not self.input.content:
            self.message.update("Error. Enter the task first", error=True)
            return
        if self.focus.timer.paused:
            self.message.update("Paused")
        else:
            self.message.update("Running")
        self.focus.switch_timer()

    async def action_restart(self):
        self.focus.save_data()
        self.table.collect_data()
        await self.scroll.update(self.table)
        self.focus.restart_timer()
        self.message.update("Your data saved. Timer restarted")

    async def action_new_task(self):
        if self.focus.timer.on:
            self.message.update("Timer is running. "
                                "To start new task restart the timer first.",
                                error=True)
        else:
            await self.input.focus()
            self.input.focused(True)
            self.message.update("Enter the task and press enter")

    async def action_submit(self):
        if not self.input.content:
            self.message.update("Error. Empty task", error=True)
        else:
            self.focus.switch_timer()
            self.message.update("Running")
            self.focus.task_name = self.input.content

        self.input.focused(False)
        await self.focus.focus()


MyApp.run(title="Time tracker", log="textual.log")
