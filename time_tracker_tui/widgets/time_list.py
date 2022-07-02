from rich.padding import PaddingDimensions
from rich.text import TextType
from textual.widgets import TreeNode
from widgets.nested_list import NestedList
import db


class TimeList(NestedList):
    def __init__(
        self,
        label: TextType,
        data: tuple,
        name: str | None = None,
        padding: PaddingDimensions = (1, 1),
    ) -> None:
        super().__init__(label=label, data=data, name=name, padding=padding)

    async def on_mount(self) -> None:
        await self.collect_data()

    async def collect_data(self) -> None:
        self._data = db.fetch_full_info()
        await self.build_tree()
        await self.root.expand()
        await self.go_down()

    async def build_tree(self, root_id: int = 0) -> None:
        for row in self._data:
            if row[1] == root_id:
                await self.add(self.cursor, row[2], row)
                await self.nodes[self.cursor].toggle()
                await self.cursor_down()
                await self.build_tree(row[0])
                await self.cursor_up()
                await self.nodes[self.cursor].toggle()

    def add_task(self) -> None:
        pass

    def add_session(self) -> None:
        pass

    def delete_task(self) -> None:
        pass
    
    def render_node(self, node: TreeNode) -> None:
        pass

