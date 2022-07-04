from rich.padding import PaddingDimensions
from rich.text import Text, TextType
from textual.widgets import NodeID, TreeControl


class NestedList(TreeControl):
    def __init__(
        self,
        label: TextType,
        data: tuple,
        name: str | None = None,
        padding: PaddingDimensions = (1, 1),
    ) -> None:
        super().__init__(label, data, name=name, padding=padding)
        # self._tree.hide_root = True
        self.show_cursor = True

    async def add_child(self, data: tuple, label: TextType = "") -> None:
        await self.add(self.cursor, label=label, data=data)
        await self.nodes[self.cursor].expand()
        await self._cur_to_latest_child()

    async def add_sibling(self, data: tuple, label: TextType = "") -> None:
        node = self.nodes[self.cursor]
        parent = node.parent
        if parent:
            await self.add(parent.id, label=label, data=data)
            await self._cur_to_latest_child()

    async def add_root_child(self, data: tuple, label: TextType = "") -> None:
        await self.add(self.root.id, label=label, data=data)
        await self._cur_to_latest_child()

    async def remove_node(self) -> None:
        node = self.nodes[self.cursor]
        parent = node.parent
        if parent:
            if node.next_sibling:
                await self._cur_to_next_sibling()
            else:
                await self.cursor_up()
            parent.children.remove(node)
            parent.tree.children.remove(node.tree)

        self.refresh(layout=True)

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
