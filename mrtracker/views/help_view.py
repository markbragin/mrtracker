from rich.align import Align
from rich.table import Table
from textual.views._dock_view import DockView

from ..config import CONFIG_PATH, config
from ..widgets.simple_scrollview import SimpleScrollView


class HelpView(DockView):
    def __init__(self, name: str | None = "HelpView") -> None:
        super().__init__(name=name)
        table = self.create_table()
        self.scrll = SimpleScrollView(Align(table, "center"))

    async def on_mount(self) -> None:
        await self.dock(self.scrll)

    def create_table(self) -> Table:
        # ---------------------------------------
        table = Table(show_header=False, box=None)
        table.title_style = ""
        table.title = (
            "[yellow bold]Help\n\n[/]"
            + "To change bindings and styles edit\n"
            + f"[dim]{CONFIG_PATH}[/]"
        )

        # --------------------------------------
        table.add_row("[magenta]App keys:")
        for descrip, key in config.app_keys.items():
            table.add_row(
                Align(key, "right", style="blue"), " ".join(descrip.split("_"))
            )
        table.add_row(end_section=True)

        # -------------------------------------
        table.add_row("[magenta]Tasklist keys:")
        for descrip, key in config.tasklist_keys.items():
            table.add_row(
                Align(key, "right", style="blue"),
                " ".join(descrip.split("_")),
            )
        return table
