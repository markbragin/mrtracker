from typing import Union

from textual.widget import Widget
from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Static

from ..styles import styles


class Footer(Widget, can_focus=False):
    def __init__(self, ) -> None:
        super().__init__(name="Footer")
        self._key_text: Union[Text, None] = None

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            no_wrap=False,
            overflow="ellipsis",
            justify="center",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            if not binding.key.startswith("ctrl+"):
                continue
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(f" {key_display}-{binding.description}")
            text.append_text(key_text)
        return text

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        return Static(self._key_text, style=styles["FOOTER"])
