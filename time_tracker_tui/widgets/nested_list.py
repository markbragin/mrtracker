from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.text import TextType, Text
from textual.widgets import TreeControl


class NestedList(TreeControl):
    def __init__(
        self,
        label: TextType,
        data: tuple,
        name: str | None = None,
        padding: PaddingDimensions = (1, 1),
    ) -> None:
        super().__init__(label, data, name=name, padding=padding)
        self._tree.hide_root = True
        self.show_cursor = True

    async def add_child(self, label: TextType, data: RenderableType) -> None:
        await self.add(self.cursor, label=label, data=data)
        await self.nodes[self.cursor].expand()
        await self.go_to_latest_child()

    async def add_sibling(self, label: TextType, data: RenderableType) -> None:
        node = self.nodes[self.cursor]
        parent = node.parent
        if parent:
            await self.add(parent.id, label=label, data=data)

    async def remove_node(self) -> None:
        node = self.nodes[self.cursor]
        parent = node.parent
        if parent:
            if node.next_sibling:
                await self.go_to_next_sibling()
            else:
                await self.cursor_up()
            parent.children.remove(node)
            parent.tree.children.remove(node.tree)

        self.refresh(layout=True)

    async def go_to_latest_child(self) -> None:
        self._remove_hl()
        await self._cur_to_latest_child()
        self._highlight()

    async def _cur_to_latest_child(self) -> None:
        node_id = self.id
        while self.cursor != node_id:
            await self.cursor_down()

    async def go_to_parent(self) -> None:
        self._remove_hl()
        await self._cur_to_parent()
        self._highlight()

    async def _cur_to_parent(self) -> None:
        node = self.nodes[self.cursor]
        parent = node.parent
        if parent is self.root:
            return

        if parent:
            while self.cursor != parent.id:
                await self.cursor_up()

    async def go_to_next_sibling(self) -> None:
        self._remove_hl()
        await self._cur_to_next_sibling()
        self._highlight()

    async def _cur_to_next_sibling(self) -> None:
        node = self.nodes[self.cursor]
        sibling = node.next_sibling
        if sibling:
            while self.cursor != sibling.id:
                await self.cursor_down()

    async def cur_to_root(self) -> None:
        while self.cursor != self.root.id:
            await self.cursor_up()

    async def go_down(self) -> None:
        self._remove_hl()
        await self.cursor_down()
        self._highlight()

    async def go_up(self) -> None:
        node = self.nodes[self.cursor]
        if node.previous_node is self.root:
            return

        self._remove_hl()
        await self.cursor_up()
        self._highlight()

    def _highlight(self) -> None:
        node = self.nodes[self.cursor]
        if isinstance(node.label, str):
            node.label = Text(node.label, style="reverse")
        elif isinstance(node.label, Text):
            node.label.style = "reverse"

    def _remove_hl(self) -> None:
        node = self.nodes[self.cursor]
        if isinstance(node.label, str):
            node.label = Text(node.label, style="")
        elif isinstance(node.label, Text):
            node.label.style = ""
