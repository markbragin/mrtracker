from rich.console import RenderableType
from textual.app import events
from textual.message import Message
from textual.widgets import ScrollView


class SimpleScrollView(ScrollView):
    async def update(self, content: RenderableType) -> None:
        await super().update(content)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "j":
            self.page_down()
        elif event.key == "k":
            self.page_up()

    async def handle_window_change(self, message: Message) -> None:
        message.stop()

        virtual_width, virtual_height = self.window.virtual_size
        width, height = self.size

        self.x = self.validate_x(self.x)
        self.y = self.validate_y(self.y)

        self.hscroll.virtual_size = virtual_width
        self.hscroll.window_size = width
        self.vscroll.virtual_size = virtual_height
        self.vscroll.window_size = height
