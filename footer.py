from typing import Union

from textual.widget import Widget
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text


class Footer(Widget):
    def __init__(self, border_style="", style="") -> None:
        super().__init__()
        self._key_text: Union[Text, None] = None
        self.border_style = border_style
        self.style = style

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style="white",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(
                    f"{key_display}-{binding.description} ",
                    style=self.style
            )
            text.append_text(key_text)
        return text

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        return Panel(self._key_text, border_style=self.border_style)
