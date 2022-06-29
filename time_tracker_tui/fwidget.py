from __future__ import annotations

from textual.reactive import Reactive
from textual.widget import Widget
from textual import events


class Fwidget(Widget, can_focus=True):

    _has_focus: Reactive[bool] = Reactive(False)

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name=name)

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    async def _unfocus(self) -> None:
        await self.app.set_focus(None)
