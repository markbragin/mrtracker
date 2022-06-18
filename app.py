from textual.app import App
from textual.widgets import Placeholder
from textual.widgets import Header
from rich.text import Text
from rich.table import Table

from footer import Footer
from time_table import TimeTable
from process import Process


class MyApp(App):

    async def on_load(self) -> None:
        await self.bind("q", "quit", "quit")
        await self.bind("p", "switch", "pause/resume")
        await self.bind("r", "restart", "restart")

    async def on_mount(self) -> None:
        self.header = Header(style="red")
        self.footer = Footer(border_style="red", style="red")
        self.process = Process(border_style="red", style="red")
        self.table = TimeTable(border_style="red", h_style="red", r_style="red")

        grid = await self.view.dock_grid()
        grid.add_column("left", fraction=1)
        grid.add_column("right", fraction=2)
        grid.add_row("header", fraction=1, size=3)
        grid.add_row("content", fraction=1)
        grid.add_row("footer", fraction=1, size=3)
        grid.add_areas(
            header="left-start|right-end,header",
            area1="left,content",
            area2="right,content",
            footer="left-start|right-end,footer"
        )
        grid.place(
            header=self.header,
            area1=self.process,
            area2=self.table,
            footer=self.footer
        )

    async def action_switch(self):
        self.process.timer.switch()

    async def action_restart(self):
        self.process.timer.restart()


MyApp.run(title="Time tracker")
