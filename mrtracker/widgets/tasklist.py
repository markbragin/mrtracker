from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.reactive import Reactive, events
from textual.widgets import NodeID, TreeNode

from .. import db
from ..config import config
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
        data: Entry = generate_empty_entry(0, -1),
        name: str | None = None,
        padding: PaddingDimensions = 0,
    ) -> None:
        super().__init__(label=label, data=data, name=name, padding=padding)
        self._tree.hide_root = True

    async def on_mount(self) -> None:
        await self.collect_data()

    async def collect_data(self) -> None:
        self._data = db.fetch_full_info()
        self._next_task_id = db.get_max_task_id() + 1
        await self._build_tree()
        await self.root.expand()

    async def _build_tree(self) -> None:
        for row in self._data:
            await self.add(row[1], row[2], Entry(row))

        self.sum_time_recursively()

    def sum_time_recursively(self, node_id: NodeID = NodeID(0)) -> tuple:
        cur = self.nodes[node_id]
        collected_data = (0, 0, 0)

        for node in cur.children:
            child_data = self.sum_time_recursively(node.id)
            collected_data = self.sum_tuples(collected_data, child_data)

        cur.data.today += collected_data[0]
        cur.data.month += collected_data[1]
        cur.data.total += collected_data[2]

        return (cur.data.today, cur.data.month, cur.data.total)

    def sum_tuples(self, t1, t2) -> tuple:
        return tuple(map(sum, zip(t1, t2)))

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
        self._mode = Mode.NORMAL

    async def on_key(self, event: events.Key) -> None:
        if self._mode == Mode.INSERT:
            await self.handle_keypress_in_insert_mode(event)
        elif self._mode == Mode.DELETE:
            await self.handle_keypress_in_delete_mode(event)
        else:
            await self.handle_keypress_in_normal_mode(event)

    async def handle_keypress_in_insert_mode(self, event: events.Key) -> None:
        entry = self.nodes[self.cursor].data
        entry.on_key(event)
        if event.key in ["escape", "enter"]:
            self._mode = Mode.NORMAL
            old_name = entry.name
            entry.name = entry.content
            if entry.name == "":
                await self.remove_childless_node()
            elif entry.task_id == self._next_task_id:
                db.add_task(entry.name, entry.parent_id)
                self._next_task_id += 1
                ialogger.update(
                    f"{entry.type.name} [{config.styles['LOGGER_HIGHLIGHT']}]"
                    f"{entry.name}[/] added."
                )
            elif entry.name != old_name:
                db.rename_task(entry.task_id, entry.name)
                ialogger.update(
                    f"{entry.type.name} renamed "
                    f"[{config.styles['LOGGER_HIGHLIGHT']}]{old_name}[/] ->"
                    f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.name}[/]."
                )

        event.stop()
        self.refresh()

    async def handle_keypress_in_delete_mode(self, event: events.Key) -> None:
        entry = self.nodes[self.cursor].data
        entry.on_key(event)
        if event.key == "enter":
            self._mode = Mode.NORMAL
            if entry.content == "delete":
                db.delete_tasks(*await self._delete_tasks_recursively())
                self._next_task_id = db.get_max_task_id() + 1
                ialogger.update(
                    f"{entry.type.name} [{config.styles['LOGGER_HIGHLIGHT']}]"
                    + f"{entry.name}[/] has been removed."
                )
            else:
                ialogger.update("Deletion canceled")
        elif event.key == "escape":
            self._mode = Mode.NORMAL
            ialogger.update("Deletion canceled")

        event.stop()
        self.refresh()

    async def handle_keypress_in_normal_mode(self, event: events.Key) -> None:
        key = event.key.translate(cyrillic_layout)
        if event.key in config.tasklist_keys["start_task"]:
            self._handle_starting_task()
        elif self.blocked:
            return
        elif key in config.tasklist_keys["rename_task"]:
            self.rename_task()
        elif key in config.tasklist_keys["go_down"]:
            await self.go_down()
        elif key in config.tasklist_keys["go_up"]:
            await self.go_up()
        elif key in config.tasklist_keys["toggle_folding"]:
            await self.toggle_folding()
        elif key in config.tasklist_keys["toggle_folding_recursively"]:
            await self.toggle_folding_recursively()
        elif key in config.tasklist_keys["go_to_parent"]:
            await self.go_to_parent()
        elif key in config.tasklist_keys["go_to_parent_folder"]:
            await self.go_to_parent_folder()
        elif key in config.tasklist_keys["add_folder"]:
            await self.add_folder()
        elif key in config.tasklist_keys["add_child_task"]:
            await self.add_child_task()
        elif key in config.tasklist_keys["add_sibling_task"]:
            await self.add_sibling_task()
        elif key in config.tasklist_keys["delete_task"]:
            await self.delete_task()
        elif key in config.tasklist_keys["toggle_all_folders"]:
            await self.toggle_all_folders()

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

    def rename_task(self) -> None:
        if not self._valid_cursor():
            return
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.content = entry.name

    async def add_child(self, label: TextType, data) -> None:
        if self.cursor == self.root.children[0].id:
            return
        await super().add_child(label, data)

    async def add_sibling(self, label: TextType, data) -> None:
        if not self._valid_cursor():
            return
        await super().add_sibling(label, data)

    async def add_folder(self) -> None:
        await self.add_root_child(
            "", generate_empty_entry(self._next_task_id, 0)
        )
        await self.on_key(events.Key(self, "r"))

    async def add_child_task(self) -> None:
        if not self._valid_cursor():
            ialogger.update("Create project first", error=True)
            return
        entry = self.nodes[self.cursor].data
        await self.add_child(
            "", generate_empty_entry(self._next_task_id, entry.task_id)
        )
        await self.on_key(events.Key(self, "r"))

    async def add_sibling_task(self) -> None:
        if not self._valid_cursor():
            ialogger.update("Create project first", error=True)
            return
        entry = self.nodes[self.cursor].data
        await self.add_sibling(
            "", generate_empty_entry(self._next_task_id, entry.parent_id)
        )
        await self.on_key(events.Key(self, "r"))

    async def delete_task(self) -> None:
        if not self._valid_cursor():
            return
        self._mode = Mode.DELETE
        hl = config.styles["LOGGER_HIGHLIGHT"]
        ialogger.update(f"Type [{hl}]'delete'[/] and press [{hl}]enter[/]")
        self.nodes[self.cursor].data.clear_content()

    def _valid_cursor(self) -> bool:
        return self.cursor not in [self.root.id, self.root.children[0].id]

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

    async def toggle_all_folders(self) -> None:
        if self.root.children[1]:
            for node in self.root.children:
                await node.expand(not self.root.children[-1].expanded)
            await self.go_to_parent_folder()

    def render(self) -> RenderableType:
        return Panel(self._tree, border_style=config.styles["TASKLIST_BORDER"])

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
            style = config.styles["HIGHLIGHTED_TASK"]
        else:
            rendr = node.data.render(expanded=node.expanded)
            style = config.styles["NORMAL_TASK"]
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
        header.add_row(name, time, style=config.styles["TASKLIST_HEADER"])
        return header

    def _render_root(self) -> RenderableType:
        return self.root.label
