from textual.widget import Widget
from rich.text import Text
from rich.table import Table
from rich.panel import Panel


class TimeTable(Widget):
    def __init__(self, border_style="", h_style="", r_style="") -> None:
        super().__init__()
        self.border_style = border_style
        self.h_style = h_style
        self.r_style = r_style

        self.table = Table(
            box=None,
            expand=True,
            header_style=self.h_style,
            row_styles=[r_style],
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
                border_style=self.border_style,
                expand=True,
                )

    def render(self) -> Panel:
        return self.content



