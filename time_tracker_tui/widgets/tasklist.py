from __future__ import annotations

from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.reactive import Reactive, events
from textual.widgets import TreeNode

from .. import db
from ..mode import Mode
from .entry import Entry, EntryType, generate_empty_entry
from .in_app_logger import ialogger
from .nested_list import NestedList


cyrillic_layout = dict(
    zip(
        map(
            ord,
            "йцукенгшщзхъфывапролджэячсмитьбю.ё"
            "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
        ),
        "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
        'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~',
    )
)


class TaskList(NestedList):

    _mode: Reactive[Mode] = Reactive(Mode.NORMAL)
    _next_task_id: int = 0
    current_task: Reactive[Entry | None] = Reactive(None)
    blocked: Reactive[bool] = Reactive(False)

    def __init__(
        self,
        label: TextType = "TaskList",
        data=[],
        name: str | None = None,
        padding: PaddingDimensions = (0, 1),
    ) -> None:
        super().__init__(label=label, data=data, name=name, padding=padding)
        self._tree.hide_root = True
        self._hl_style = "yellow"
        self._dim_style = "white"

    async def on_mount(self) -> None:
        await self.add(self.root.id, "Header", ())
        await self.collect_data()

    async def collect_data(self) -> None:
        self._data = db.fetch_full_info()
        self._next_task_id = db.get_max_task_id() + 1
        await self._build_tree()
        await self.root.expand()

    async def _build_tree(self, node_id: int = 0) -> tuple:
        collected_data = (0, 0, 0)
        for row in self._data:
            if row[1] == node_id:
                await self.add_child(row[2], Entry(row))
                sub = await self._build_tree(row[0])
                collected_data = self.sum_tuples(collected_data, sub)
                await self._cur_to_parent()
                await self.nodes[self.cursor].toggle()

        if node_id == 0:
            return tuple()

        entry = self.nodes[self.cursor].data
        entry.today, entry.month, entry.total = self.sum_tuples(
            (entry.today, entry.month, entry.total), collected_data
        )
        return entry.today, entry.month, entry.total

    def sum_tuples(self, t1, t2) -> tuple:
        no_none1 = tuple(x if x is not None else 0 for x in t1)
        no_none2 = tuple(x if x is not None else 0 for x in t2)
        return tuple(map(sum, zip(no_none1, no_none2)))

    async def go_down(self) -> None:
        await self.cursor_down()

    async def go_up(self) -> None:
        if self.nodes[self.cursor].previous_node is not self.root.children[0]:
            await self.cursor_up()

    async def go_to_parent(self) -> None:
        if self.nodes[self.cursor].parent in [None, self.root]:
            return
        parent = self.nodes[self.cursor].parent
        while self.cursor != parent.id:
            await self.cursor_up()

    async def go_to_parent_folder(self) -> None:
        if self.nodes[self.cursor].parent in [None, self.root.id]:
            return
        while self.nodes[self.cursor].parent is not self.root:
            await self.cursor_up()

    async def on_focus(self) -> None:
        await self.go_down()
        await self.go_down()
        self._mode = Mode.NORMAL

    async def on_blur(self) -> None:
        await self._cur_to_root()

    async def on_key(self, event: events.Key) -> None:
        if self._mode == Mode.INSERT:
            await self.handle_keypress_in_insert_mode(event)
        else:
            await self.handle_keypress_in_normal_mode(event)

    async def handle_keypress_in_insert_mode(self, event: events.Key) -> None:
        entry = self.nodes[self.cursor].data
        old_name = entry.name
        entry.on_key(event)
        if event.key in ["escape", "enter"]:
            self._toggle_mode()
            entity = "Project" if entry.type == EntryType.FOLDER else "Task"
            if entry.name == "":
                await self.remove_childless_node()
            elif entry.task_id == self._next_task_id:
                db.add_task(entry.name, entry.parent_id)
                self._next_task_id += 1
                ialogger.update(f"{entity} [magenta]{entry.name}[/] added.")
            else:
                db.rename_task(entry.task_id, entry.name)
                ialogger.update(
                    f"{entity} renamed [magenta]{old_name}[/]"
                    f" -> [magenta]{entry.name}[/]."
                )

        event.stop()
        self.refresh()

    async def handle_keypress_in_normal_mode(self, event: events.Key) -> None:
        key = event.key.translate(cyrillic_layout)
        if event.key == "enter":
            self._handle_starting_task()
        elif self.blocked:
            return
        elif key == "r":
            self.rename_task()
        elif key in ["j", "down"]:
            await self.go_down()
        elif key in ["k", "up"]:
            await self.go_up()
        elif key == "z":
            await self.toggle_folding()
        elif key == "Z":
            await self.toggle_folding_recursively()
        elif key == "p":
            await self.go_to_parent()
        elif key == "P":
            await self.go_to_parent_folder()
        elif key == "n":
            await self.add_folder()
        elif key == "a":
            await self.add_child_task()
        elif key == "s":
            await self.add_sibling_task()
        elif key == "x":
            await self.delete_task()

    def _handle_starting_task(self) -> None:
        if self.blocked:
            ialogger.update(
                "[b]Timer is running[/]. "
                "To start new task restart the timer first.",
                error=True,
            )
            return
        else:
            entry = self.nodes[self.cursor].data
            if entry.type is EntryType.FOLDER:
                ialogger.update("Select task, not project", error=True)
            else:
                self.current_task = entry

    def _toggle_mode(self) -> None:
        self._mode = Mode.INSERT if self._mode == Mode.NORMAL else Mode.NORMAL

    def rename_task(self) -> None:
        if self.cursor in [self.root.id, self.root.children[0].id]:
            return
        self._toggle_mode()
        entry = self.nodes[self.cursor].data
        entry.content = entry.name

    async def add_child(self, label: TextType, data) -> None:
        if self.cursor == self.root.children[0].id:
            return
        await super().add_child(label, data)

    async def add_sibling(self, label: TextType, data) -> None:
        if self.cursor in [self.root.id, self.root.children[0].id]:
            return
        await super().add_sibling(label, data)

    async def add_folder(self) -> None:
        await self.add_root_child(
            "", generate_empty_entry(self._next_task_id, 0)
        )
        await self.on_key(events.Key(self, "r"))

    async def add_child_task(self) -> None:
        if self.cursor in [self.root.id, self.root.children[0].id]:
            ialogger.update("Create project first", error=True)
            return
        entry = self.nodes[self.cursor].data
        await self.add_child(
            "", generate_empty_entry(self._next_task_id, entry.task_id)
        )
        await self.on_key(events.Key(self, "r"))

    async def add_sibling_task(self) -> None:
        if self.cursor in [self.root.id, self.root.children[0].id]:
            ialogger.update("Create project first", error=True)
            return
        entry = self.nodes[self.cursor].data
        await self.add_sibling(
            "", generate_empty_entry(self._next_task_id, entry.parent_id)
        )
        await self.on_key(events.Key(self, "r"))

    async def delete_task(self) -> None:
        if self.cursor in [self.root.id, self.root.children[0].id]:
            return
        entry = self.nodes[self.cursor].data
        db.delete_tasks(*await self._delete_tasks_recursively())
        self._next_task_id = db.get_max_task_id() + 1

        entity = "Project" if entry.type is EntryType.FOLDER else "Task"
        ialogger.update(f"{entity} [magenta]{entry.name}[/] has been removed.")

    async def _delete_tasks_recursively(self) -> list[int]:
        node = self.nodes[self.cursor]
        ids = [node.data.task_id]

        if node.data.type is EntryType.TASK:
            self.subtract_child_time(node)

        await node.expand()
        while node.children:
            await self.cursor_down()
            cur_node = self.nodes[self.cursor]
            ids.append(cur_node.data.task_id)
            if not cur_node.children:
                await self.remove_childless_node()
                continue
            await cur_node.expand()

        await self.remove_childless_node()
        await self.cursor_down()
        return ids

    def subtract_child_time(self, child: TreeNode) -> None:
        if child.parent:
            child.parent.data.today -= child.data.today
            child.parent.data.month -= child.data.month
            child.parent.data.total -= child.data.total

    async def add_time(self, seconds: int) -> None:
        entry = self.nodes[self.cursor].data
        entry.today += seconds
        entry.month += seconds
        entry.total += seconds
        if entry.type is EntryType.FOLDER:
            return
        await self.go_to_parent()
        await self.add_time(seconds)

    def render(self) -> RenderableType:
        return Panel(self._tree, border_style="blue")

    def render_node(self, node: TreeNode) -> RenderableType:
        if node is self.root:
            return self._render_root()
        elif node is self.root.children[0]:
            return self._render_header()
        else:
            return self._render_entry(node)

    def _render_entry(self, node: TreeNode) -> RenderableType:
        if node.id == self.cursor:
            rendr = node.data.render(mode=self._mode, expanded=node.expanded)
            style = self._hl_style
        else:
            rendr = node.data.render(expanded=node.expanded)
            style = self._dim_style
        rendr.row_styles = [style]
        return rendr

    def _render_header(self) -> RenderableType:
        text_data = (
            "Today".rjust(15, " ")
            + "Month".rjust(12, " ")
            + "Total".rjust(12, " ")
        )

        name = Text("Projects", justify="left")
        time = Text(text_data, justify="right")

        header = Table.grid(expand=True)
        header.add_row(name, time, style="magenta bold")
        return header

    def _render_root(self) -> RenderableType:
        return self.root.label
