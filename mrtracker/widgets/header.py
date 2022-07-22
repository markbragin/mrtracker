from datetime import datetime

from rich.console import RenderableType
from rich.table import Table
from textual.reactive import Reactive, watch
from textual.widget import Widget

from ..config import config


class MyHeader(Widget):
    def __init__(self) -> None:
        super().__init__()

    clock: Reactive[bool] = Reactive(True)
    title: Reactive[str] = Reactive("")
    sub_title: Reactive[str] = Reactive("")

    @property
    def full_title(self) -> str:
        return (
            f"{self.title} - {self.sub_title}"
            if self.sub_title
            else self.title
        )

    def get_clock(self) -> str:
        return datetime.now().time().strftime("%X")

    def render(self) -> RenderableType:
        header_table = Table.grid(padding=(0, 1), pad_edge=True, expand=True)
        header_table.row_styles = [config.styles["HEADER"]]
        header_table.add_column(justify="left", ratio=0, width=8)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right", width=8)
        header_table.add_row(
            "⏱️", self.full_title, self.get_clock() if self.clock else ""
        )
        return header_table

    async def on_mount(self) -> None:
        self.set_interval(1.0, callback=self.refresh)

        async def set_title(title: str) -> None:
            self.title = title

        async def set_sub_title(sub_title: str) -> None:
            self.sub_title = sub_title

        watch(self.app, "title", set_title)
        watch(self.app, "sub_title", set_sub_title)
