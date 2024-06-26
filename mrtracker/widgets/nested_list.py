from rich.padding import PaddingDimensions
from rich.text import TextType
from textual.app import events
from textual.widgets import NodeID, TreeControl, TreeNode


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
        self._cur_to_latest_child()

    async def add_sibling(self, label: TextType, data) -> None:
        node = self.nodes[self.cursor]
        if node is self.root:
            return
        self._cur_to_parent()
        await self.add_child(label, data)

    async def add_root_child(self, label: TextType, data) -> None:
        await self._cur_to_root()
        await self.add_child(label, data)

    async def remove_node(self, node: TreeNode | None = None) -> None:
        node = node if node else self.nodes[self.cursor]

        if node is self.root:
            return

        for nd in node.children:
            await self.remove_node(nd)

        if node.id == self.cursor:
            await self.cursor_up()

        node.parent.tree.children.remove(node.tree)
        node.parent.children.remove(node)
        del self.nodes[node.id]
        self.id = max(self.nodes.keys())

    def _cur_to_latest_child(self) -> None:
        self.cursor = self.id

    def _cur_to_parent(self) -> None:
        parent = self.nodes[self.cursor].parent
        self.cursor = parent.id if parent else self.cursor

    def _cur_up_to_root_child(self) -> None:
        while self.nodes[self.cursor].parent is not self.root:
            self._cur_to_parent()

    async def _cur_to_next_sibling(self) -> None:
        sibling = self.nodes[self.cursor].next_sibling
        if sibling:
            while self.cursor != sibling.id:
                await self.cursor_down()

    async def _cur_to_root(self) -> None:
        self.cursor = NodeID(0)
        self.cursor_line = 0

    async def toggle_folding(self) -> None:
        await self.nodes[self.cursor].toggle()

    async def key_down(self, event: events.Key) -> None:
        pass

    async def key_up(self, event: events.Key) -> None:
        pass

    async def key_enter(self, event: events.Key) -> None:
        pass
