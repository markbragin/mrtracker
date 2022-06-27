from rich.console import RenderableType
from rich.table import Table
from rich.panel import Panel

from .. import db
from ..fwidget import Fwidget
from ..styles import styles
from ..stopwatch import Stopwatch as time


class TimeTable(Fwidget):
    def __init__(self):
        super().__init__(name="TimeTable")
        self.collect_data()

    def collect_data(self) -> None:
        self.table = Table(
            box=None,
            expand=True,
            header_style=styles["TIME_TABLE_HEADER"],
            row_styles=[styles["TIME_TABLE_TEXT"]],
        )

        self.table.add_column(header="ID", max_width=3)
        self.table.add_column(header="Task")
        self.table.add_column(header="Today")
        self.table.add_column(header="This month")
        self.table.add_column(header="Total")

        data = db.fetch_full_info()
        for id, row in enumerate(data, start=1):
            self.table.add_row(
                f"{id}",
                row[0],
                time.sec_to_str(row[1]) if row[1] else time.sec_to_str(0),
                time.sec_to_str(row[2]) if row[2] else time.sec_to_str(0),
                time.sec_to_str(row[3]) if row[3] else time.sec_to_str(0),
            )

        self.panel = Panel(
            self.table,
            title="Time table",
            border_style=styles["TIME_TABLE_BORDER"],
            expand=True,
        )

        self.refresh()

    def render(self) -> RenderableType:
        return self.panel
