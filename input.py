from textual.widget import Widget
from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual import events

from styles import styles


class Input(Widget):
    def __init__(self) -> None:
        super().__init__(name="Input")
        self.content = ""
        self._has_focus = False
        self._border_style = styles["INPUT_BORDER_BAD"]
        self._text_style = styles["INPUT_LOST_FOCUS"]

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+h":
            if self.content:
                self.content = self.content[:-1]
        if event.key in ["enter", "escape"] or "ctrl+" in event.key:
            pass
        else:
            self.content += event.key
        self.refresh()

    def focused(self, focused: bool):
        if focused:
            self.content = ""
        self._has_focus = focused
        self.refresh()

    def render(self):
        if self._has_focus:
            self._text_style = styles["INPUT_HAS_FOCUS"]
        else:
            self._text_style = styles["INPUT_LOST_FOCUS"]
        if self.content:
            rendr = Align.center(Text(self.content), style=self._text_style)
            self._border_style = styles["INPUT_BORDER_GOOD"]
        else:
            rendr = Align.center(Text("Enter your task"),
                                 style=self._text_style)
            self._border_style = styles["INPUT_BORDER_BAD"]

        self.panel = Panel(
            rendr,
            title="Working on",
            border_style=self._border_style,
            height=3
        )
        return self.panel
