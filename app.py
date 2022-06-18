from textual.app import App
from textual.widgets import Header
from footer import Footer
from time_table import TimeTable
from focus import Focus

from styles import styles


class MyApp(App):

    async def on_load(self) -> None:
        await self.bind("q", "quit", "quit")
        await self.bind("p", "switch", "pause/resume")
        await self.bind("r", "restart", "restart")

    async def on_mount(self) -> None:
        self.header = Header(style=styles["HEADER"])
        self.footer = Footer()
        self.focus = Focus()
        self.table = TimeTable()

        grid = await self.view.dock_grid()
        grid.add_column("left", fraction=1)
        grid.add_column("right", fraction=3)
        grid.add_row("header", fraction=1, size=3)
        grid.add_row("content", fraction=1)
        grid.add_row("footer", fraction=1, size=1)
        grid.add_areas(
            header="left-start|right-end,header",
            area1="left,content",
            area2="right,content",
            footer="left-start|right-end,footer"
        )
        grid.place(
            header=self.header,
            area1=self.focus,
            area2=self.table,
            footer=self.footer
        )

    async def action_switch(self):
        self.focus.timer.switch()

    async def action_restart(self):
        self.focus.timer.restart()


MyApp.run(title="Time tracker")
