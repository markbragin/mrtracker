from rich.padding import PaddingDimensions
from rich.text import Text, TextType
from textual.widgets import NodeID, TreeControl


class NestedList(TreeControl):
    def __init__(
        self,
        label: TextType,
        data,
        name: str | None = None,
        padding: PaddingDimensions = (1, 1),
    ) -> None:
        super().__init__(label, data, name=name, padding=padding)
        self.show_cursor = True

    async def add_child(self, label: TextType, data) -> None:
        await self.add(self.cursor, label=label, data=data)
        await self.nodes[self.cursor].expand()
        await self._cur_to_latest_child()

    async def add_sibling(self, label: TextType, data) -> None:
        node = self.nodes[self.cursor]
        if node is self.root:
            return
        await self._cur_to_parent()
        await self.add_child(label, data)

    async def add_root_child(self, label: TextType, data) -> None:
        await self._cur_to_root()
        await self.add_child(label, data)

    async def remove_childless_node(self) -> None:
        if self.cursor == self.root.id:
            return

        node = self.nodes[self.cursor]
        await self.cursor_up()
        node.parent.tree.children.remove(node.tree)
        node.parent.children.remove(node)
        del self.nodes[node.id]

    async def _cur_to_latest_child(self) -> None:
        node_id = self.id
        while self.cursor != node_id:
            await self.cursor_down()

    async def _cur_to_parent(self) -> None:
        parent = self.nodes[self.cursor].parent
        if parent:
            while self.cursor != parent.id:
                await self.cursor_up()

    async def _cur_to_next_sibling(self) -> None:
        sibling = self.nodes[self.cursor].next_sibling
        if sibling:
            while self.cursor != sibling.id:
                await self.cursor_down()

    async def _cur_to_root(self) -> None:
        self.cursor = NodeID(0)
        self.cursor_line = 0
