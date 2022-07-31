from rich.align import Align
from rich.table import Table
from textual.app import events
from textual.views._dock_view import DockView

from ..config import CONFIG_PATH, config
from ..widgets.simple_scrollview import SimpleScrollView


class HelpView(DockView):
    def __init__(self, name: str | None = "HelpView") -> None:
        super().__init__(name=name)
        self.create_table()
        self.scrll = SimpleScrollView(Align(self.table, "center"))

    async def on_focus(self) -> None:
        await self.scrll.focus()

    async def on_mount(self) -> None:
        await self.dock(self.scrll)

    def create_table(self):
        self.table = Table(show_header=False, box=None)
        self.table.title_style = ""
        self._insert_title()
        self._insert_app_keys()
        self._insert_tasklist_keys()
        self._insert_stats_keys()

    def _insert_title(self) -> None:
        self.table.title = (
            "[yellow bold]Help\n\n[/]"
            + "To change bindings and styles edit\n"
            + f"[dim]{CONFIG_PATH}[/]"
        )

    def _insert_app_keys(self) -> None:
        self.table.add_row("[magenta]App keys:")
        for descrip, key in config.app_keys.items():
            self.table.add_row(
                Align(key, "right", style="blue"), " ".join(descrip.split("_"))
            )
        self.table.add_row(end_section=True)

    def _insert_tasklist_keys(self) -> None:
        self.table.add_row("[magenta]Tasklist keys:")
        for descrip, key in config.tasklist_keys.items():
            self.table.add_row(
                Align(key, "right", style="blue"),
                " ".join(descrip.split("_")),
            )
        self.table.add_row(
            Align("1, 2, 3", "right", style="blue"),
            "change format",
        )
        self.table.add_row(end_section=True)

    def _insert_stats_keys(self) -> None:
        self.table.add_row("[magenta]Tasklist keys:")
        for descrip, key in config.stats_keys.items():
            self.table.add_row(
                Align(key, "right", style="blue"),
                " ".join(descrip.split("_")),
            )


    async def on_key(self, event: events.Key) -> None:
        if event.key in [config.tasklist_keys["go_down"], "down"]:
            self.scrll.page_down()
        elif event.key in [config.tasklist_keys["go_up"], "up"]:
            self.scrll.page_up()
