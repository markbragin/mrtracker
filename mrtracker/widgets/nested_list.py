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

    async def _cur_back_to(self, node: TreeNode) -> None:
        while self.cursor != node.id:
            await self.cursor_up()

    async def _cur_to_root(self) -> None:
        self.cursor = NodeID(0)
        self.cursor_line = 0

    async def toggle_folding(self) -> None:
        await self.nodes[self.cursor].toggle()

    async def toggle_folding_recursively(
        self, node: TreeNode | None = None, expanded: bool | None = None
    ) -> None:
        node = node if node else self.nodes[self.cursor]
        expanded = expanded if expanded else not node.expanded
        await self._fold_recursively(expanded, node)

    async def _fold_recursively(self, expanded: bool, node: TreeNode) -> None:
        await node.expand(expanded)
        for nd in node.children:
            await nd.expand(expanded)
            await self._fold_recursively(expanded, nd)

    async def key_down(self, event: events.Key) -> None:
        pass

    async def key_up(self, event: events.Key) -> None:
        pass

    async def key_enter(self, event: events.Key) -> None:
        pass
