from textual.widget import Widget
from rich.text import Text
from rich.table import Table
from rich.panel import Panel

from styles import styles


class TimeTable(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.table = Table(
            box=None,
            expand=True,
            header_style=styles["TIME_TABLE_HEADER"],
            row_styles=[styles["TIME_TABLE_TEXT"]],
            )
        self.table.add_column(header="ID", ratio=1)
        self.table.add_column(header="Task", ratio=2)
        self.table.add_column(header="Time", ratio=2)
        self.table.add_row(Text("1"), Text("coding"), Text("01:00:10"))
        self.table.add_row(Text("2"), Text("math"), Text("01:00:10"))
        self.table.add_row(Text("3"), Text("cowriding"), Text("66:00:10"))

        self.content = Panel(
                self.table,
                title="Time table",
                highlight=True,
                border_style=styles["TIME_TABLE_BORDER"],
                expand=True,
                )

    def render(self) -> Panel:
        return self.content
