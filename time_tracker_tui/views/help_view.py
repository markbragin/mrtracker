from __future__ import annotations

from rich.align import Align
from rich.table import Table
from textual.views._dock_view import DockView

from ..config import config
from ..widgets.simple_scrollview import SimpleScrollView


class HelpView(DockView):
    def __init__(self, name: str | None = "HelpView") -> None:
        super().__init__(name=name)

    async def on_mount(self) -> None:
        table = self.create_table()
        await self.dock(SimpleScrollView(Align(table, "center")))

    def create_table(self) -> Table:
        table = Table(show_header=False, box=None)
        table.add_row("[magenta]App keys:")
        for descrip, key in config.app_keys.items():
            table.add_row(
                Align(key, "right", style="blue"), " ".join(descrip.split("_"))
            )
        table.add_row(end_section=True)

        table.add_row("[magenta]Tasklist keys:")
        for descrip, keys in config.tasklist_keys.items():
            table.add_row(
                Align(", ".join(keys), "right", style="blue"),
                " ".join(descrip.split("_")),
            )
        return table
