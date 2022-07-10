from __future__ import annotations

from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from textual.views._grid_view import GridView
from textual.widgets import Static


keys = {
    "escape": "reset focus/show main menu",
    "t": "switch focus to the table",
    "enter": "start task (table)",
    "ctrl+d": "delete task (table)",
    "ctrl+n": "create new task",
    "ctrl+p": "resume/pause timer",
    "ctrl+r": "save + reset timer",
    "ctrl+q": "exit",
    "ctrl+h": "show help",
}


class HelpView(GridView):
    def __init__(self, name: str | None = "HelpView") -> None:
        super().__init__(name=name)
        self.height = len(keys) + 2
        self.width = (
            max([len(x) for x in keys.keys()])
            + max([len(x) for x in keys.values()])
            + 8
        )

    async def on_mount(self) -> None:
        self.grid.add_column("left")
        self.grid.add_column("mid", size=self.width)
        self.grid.add_column("right")
        self.grid.add_row("top")
        self.grid.add_row("mid", size=self.height)
        self.grid.add_row("bottom")
        self.grid.add_areas(center="mid,mid")

        table = Table(show_header=False, box=None)
        for key, descrip in keys.items():
            table.add_row(Align(key, align="right", style="blue"), descrip)

        panel = Panel(table, expand=False)
        self.grid.place(center=Static(panel, name="Help"))
