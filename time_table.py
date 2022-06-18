from textual.widget import Widget
from rich.table import Table
from rich.panel import Panel

import db
from styles import styles
from timer import Timer


class TimeTable(Widget):
    def on_mount(self):
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
        self.table.add_column(header="Month")
        self.table.add_column(header="Total")

        data = db.fetch_full_info()
        for id, row in enumerate(data, start=1):
            self.table.add_row(
                f"{id}",
                row[0],
                Timer.sec_to_str(row[1]) if row[1] else Timer.sec_to_str(0),
                Timer.sec_to_str(row[2]) if row[2] else Timer.sec_to_str(0),
                Timer.sec_to_str(row[3]) if row[3] else Timer.sec_to_str(0),
            )

        self.panel = Panel(
            self.table,
            title="Time table",
            highlight=True,
            border_style=styles["TIME_TABLE_BORDER"],
            expand=True,
        )

        self.refresh()

    def render(self) -> Panel:
        return self.panel
