from rich.console import RenderableType
from textual.app import events
from textual.reactive import Reactive
from textual.widget import Widget


class TextInput(Widget):

    _content: Reactive[str] = Reactive("")
    _cursor_pos: Reactive[int] = Reactive(0)
    _width: Reactive[int] = Reactive(0)
    _has_focus: Reactive[bool] = Reactive(False)
    placeholder: Reactive[str] = Reactive("")

    def __init__(self, name: str | None = "TextInput") -> None:
        super().__init__(name=name)

    def on_focus(self) -> None:
        self._has_focus = True

    def on_blur(self) -> None:
        self._has_focus = False

    async def _unfocus(self) -> None:
        await self.app.set_focus(None)

    def clear_content(self) -> None:
        self._content = ""
        self._width = 0
        self._cursor_pos = 0

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, new_content: str) -> None:
        self._content = new_content
        self._width = len(new_content)
        self._cursor_pos = self._width

    @property
    def has_focus(self) -> bool:
        return self._has_focus

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+h":
            self._on_backspace()
        elif event.key == "delete":
            self._on_delete()
        elif event.key == "left":
            self._cursor_left()
        elif event.key == "escape":
            return
        elif event.key == "right":
            self._cursor_right()
        elif event.key.isprintable() and len(event.key) == 1:
            self._insert_symbol(event.key)
        else:
            return
        event.stop()

    def _insert_symbol(self, symbol: str) -> None:
        self._content = (
            self._content[: self._cursor_pos]
            + symbol
            + self._content[self._cursor_pos :]
        )
        self._width += 1
        self._cursor_right()

    def _on_backspace(self) -> None:
        if self._cursor_pos > 0:
            self._content = (
                self._content[: self._cursor_pos - 1]
                + self._content[self._cursor_pos :]
            )
            self._width -= 1
            self._cursor_left()

    def _on_delete(self) -> None:
        if self._cursor_pos == self._width - 1:
            self._content = self._content[: self._cursor_pos]
        elif self._cursor_pos < self._width - 1:
            self._content = (
                self._content[: self._cursor_pos]
                + self._content[self._cursor_pos + 1 :]
            )
        else:
            return
        self._width -= 1

    def _is_valid_pos(self, pos: int) -> bool:
        return 0 <= pos <= self._width

    def _cursor_left(self) -> None:
        if self._is_valid_pos(self._cursor_pos - 1):
            self._cursor_pos -= 1

    def _cursor_right(self) -> None:
        if self._is_valid_pos(self._cursor_pos + 1):
            self._cursor_pos += 1

    def render(self) -> RenderableType:
        if self.has_focus:
            return self._render_with_cursor()
        else:
            return self._content

    def _render_with_cursor(self) -> RenderableType:
        if self._cursor_pos == self._width:
            visible = self._content[: self._cursor_pos] + "[reverse] [/]"
        else:
            visible = (
                self._content[: self._cursor_pos]
                + f"[reverse]{self._content[self._cursor_pos]}[/]"
                + self._content[self._cursor_pos + 1 :]
            )

        return visible

    def _render_paceholder(self) -> RenderableType:
        return self.placeholder
