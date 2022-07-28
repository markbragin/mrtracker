from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.reactive import Reactive, events
from textual.widgets import NodeID, TreeNode

from .. import db
from ..config import config
from ..mode import Action, Mode
from ..stopwatch import sec_to_str
from ..timetuple import TimeTuple
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

    current_task: Reactive[Entry | None] = Reactive(None)
    blocked: Reactive[bool] = Reactive(False)
    upd_total: Reactive[bool] = Reactive(False)
    _selected: Reactive[NodeID | None] = Reactive(None)
    _mode: Reactive[Mode] = Reactive(Mode.NORMAL)
    _action: Action | None = None

    def __init__(
        self,
        label: TextType = "root",
        data: Entry = generate_empty_entry(0, -1, "f"),
        name: str | None = None,
        padding: PaddingDimensions = 0,
    ) -> None:
        super().__init__(label=label, data=data, name=name, padding=padding)
        self._tree.hide_root = True

    async def on_mount(self) -> None:
        await self.collect_data()

    async def collect_data(self) -> None:
        self._data = db.fetch_full_info()
        await self._build_tree()
        await self.root.expand()
        self.sum_time_recursively()
        self.id = max(self.nodes.keys())

    async def _build_tree(self, node_id: NodeID = NodeID(0)) -> None:
        for row in self._data:
            if row[1] == node_id:
                self.id = row[0] - 1
                await self.add(row[1], row[2], Entry(row))
                await self._build_tree(row[0])

    def sum_time_recursively(self, node_id: NodeID = NodeID(0)) -> TimeTuple:
        cur = self.nodes[node_id]
        collected_data = (0, 0, 0)

        for node in cur.children:
            child_data = self.sum_time_recursively(node.id)
            collected_data = self.sum_time(collected_data, child_data)

        cur.data.time = self.sum_time(cur.data.own_time, collected_data)
        return cur.data.time

    def sum_time(self, t1, t2) -> TimeTuple:
        return TimeTuple(*map(sum, zip(t1, t2)))

    async def go_down(self) -> None:
        await self.cursor_down()

    async def go_up(self) -> None:
        if self.nodes[self.cursor].previous_node is not self.root.children[0]:
            await self.cursor_up()
        elif self._action is Action.MOVE:
            await self.cursor_up()

    def go_to_parent(self) -> None:
        parent = self.nodes[self.cursor].parent
        if parent is not self.root:
            self._cur_to_parent()
        elif self._action is Action.MOVE:
            self.cursor = parent.id

    async def on_focus(self) -> None:
        self._mode = Mode.NORMAL

    async def on_key(self, event: events.Key) -> None:
        if self._mode == Mode.INSERT:
            await self._handle_keypress_in_insert_mode(event)
        else:
            await self._handle_keypress_in_normal_mode(event)

    async def _handle_keypress_in_insert_mode(self, event: events.Key) -> None:
        self.nodes[self.cursor].data.on_key(event)
        if event.key in ["escape", "enter"]:
            cancel = event.key == "escape"
            if self._action is Action.ADD:
                await self._handle_adding_entry(cancel)
            elif self._action is Action.RENAME:
                self._handle_renaming_entry(cancel)
            elif self._action is Action.DELETE:
                await self._handle_deleting_entry(cancel)
            elif self._action is Action.RESET:
                self._handle_resetting_task_time(cancel)
            elif self._action is Action.RESET_REC:
                self._handle_resetting_task_time(cancel, recursively=True)
            self._action = None
            self._mode = Mode.NORMAL
        event.stop()
        self.refresh()

    async def _handle_adding_entry(self, cancel: bool = False) -> None:
        entry = self.nodes[self.cursor].data
        if entry.content == entry.name == "" or cancel:
            ialogger.update("Canceled")
            await self.remove_node()
        else:
            entry.name = entry.content
            db.add_task(entry.name, entry.parent_id, entry.etype.value)
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                f"{entry.etype.name.capitalize()} [{hl}]{entry.name}[/] added."
            )

    def _handle_renaming_entry(self, cancel: bool = False) -> None:
        entry = self.nodes[self.cursor].data
        if any((cancel, not entry.content, entry.name == entry.content)):
            ialogger.update("Canceled")
            return
        else:
            ialogger.update(
                f"{entry.etype.name.capitalize()} renamed "
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.name}[/] -> "
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.content}[/]."
            )
            entry.name = entry.content
            db.rename_task(entry.task_id, entry.name)

    async def _handle_deleting_entry(self, cancel: bool = False) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if cancel:
            ialogger.update("Canceled")
        elif entry.content == "delete":
            db.delete_tasks(self._collect_task_ids())
            await self.remove_node()
            await self.go_down()
            self.sum_time_recursively()
            self.upd_total = not self.upd_total
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                f"{entry.etype.name.capitalize()} "
                + f"[{hl}]{entry.name}[/] has been removed."
            )
        else:
            ialogger.update("Canceled")

    def _handle_resetting_task_time(
        self,
        cancel: bool = False,
        recursively: bool = False,
    ) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if cancel:
            ialogger.update("Canceled")
        elif entry.content == "reset":
            if recursively:
                db.delete_sessions_by_task_ids(self._collect_task_ids())
                self._reset_time_recursively()
            else:
                db.delete_sessions_by_task_ids([entry.task_id])
                entry.reset_own_time()
            self.sum_time_recursively()
            self.upd_total = not self.upd_total
            ialogger.update(
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.name}[/] "
                + f"time has been reset {'recursively' if recursively else ''}"
            )
        else:
            ialogger.update("Canceled")

    async def _handle_keypress_in_normal_mode(self, event: events.Key) -> None:
        key = event.key.translate(cyrillic_layout)
        if event.key in ["escape", "enter"]:
            cancel = event.key == "escape"
            if self._action == Action.MOVE:
                await self._handle_moving_entry(cancel)
            elif event.key == "enter":
                self._handle_starting_task()
        elif self.blocked:
            return
        elif key in [config.tasklist_keys["go_down"], "down"]:
            await self.go_down()
        elif key in [config.tasklist_keys["go_up"], "up"]:
            await self.go_up()
        elif key == config.tasklist_keys["go_to_parent"]:
            self.go_to_parent()
        elif key == config.tasklist_keys["rename_entry"]:
            self.rename_entry()
        elif key == config.tasklist_keys["delete_entry"]:
            self.delete_entry()
        elif key == config.tasklist_keys["move_entry"]:
            self.move_entry()
        elif key == config.tasklist_keys["add_new_task"]:
            await self.add_new_entry(EntryType.TASK)
        elif key == config.tasklist_keys["add_new_folder"]:
            await self.add_new_entry(EntryType.FOLDER)
        elif key == config.tasklist_keys["add_child_task"]:
            await self.add_child_entry(EntryType.TASK)
        elif key == config.tasklist_keys["add_child_folder"]:
            await self.add_child_entry(EntryType.FOLDER)
        elif key == config.tasklist_keys["add_sibling_task"]:
            await self.add_sibling_entry(EntryType.TASK)
        elif key == config.tasklist_keys["add_sibling_folder"]:
            await self.add_sibling_entry(EntryType.FOLDER)
        elif key == config.tasklist_keys["toggle_folding"]:
            await self.toggle_folding()
        elif key == config.tasklist_keys["toggle_folding_recursively"]:
            await self.toggle_folding_recursively()
        elif key == config.tasklist_keys["toggle_all_entries_recursively"]:
            await self.toggle_all_entries_recursively()
            self._cur_up_to_root_child()
        elif key == config.tasklist_keys["reset_entry_time"]:
            self.reset_entry_time()
        elif key == config.tasklist_keys["reset_entry_time_recursively"]:
            self.reset_entry_time(recursively=True)

    async def _handle_moving_entry(self, cancel: bool) -> None:
        selected_node = self.nodes[self._selected]
        new_parent = self.nodes[self.cursor]
        if cancel:
            ialogger.update("Canceled")
        elif self._validate_move():
            self._move_to_new_parent(selected_node, new_parent)
            db.change_parent(selected_node.id, new_parent.id)
            self.sum_time_recursively()
        else:
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                f"Can't move [{hl}]{selected_node.label}[/] to "
                f"[{hl}]{new_parent.label}[/]"
            )
            return
        self._action = None
        self._selected = None
        self._tree.hide_root = True
        self.refresh(layout=True)

    def _validate_move(self) -> bool:
        node = self.nodes[self.cursor]
        selected_node = self.nodes[self._selected]
        if selected_node.data.etype is EntryType.FOLDER is not node.data.etype:
            return False
        while node is not self.root:
            if node.id == self._selected:
                return False
            node = node.parent

        return True

    def _move_to_new_parent(self, node: TreeNode, new_par: TreeNode) -> None:
        new_par.tree.children.append(node.tree)
        node.parent.tree.children.remove(node.tree)

        new_par.children.append(node)
        node.parent.children.remove(node)

        node.parent = new_par
        node.data.parent_id = new_par.data.task_id

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
            if entry.etype is EntryType.FOLDER:
                ialogger.update("Select task, not folder", error=True)
            else:
                self.current_task = entry

    async def add_new_entry(self, etype: EntryType) -> None:
        await self.add_root_child(
            f"{etype.name}",
            generate_empty_entry(self.id + 1, 0, etype.value),
        )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.clear_content()

    async def add_child_entry(self, etype: EntryType) -> None:
        if not self._valid_cursor():
            return
        node = self.nodes[self.cursor]
        entry = node.data
        if etype is EntryType.FOLDER is not node.data.etype:
            return
        await self.add_child(
            f"{etype.name}",
            generate_empty_entry(self.id + 1, entry.task_id, etype.value),
        )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        entry.clear_content()

    async def add_sibling_entry(self, etype: EntryType) -> None:
        if not self._valid_cursor():
            return
        node = self.nodes[self.cursor]
        entry = node.data
        if etype is EntryType.FOLDER is not node.parent.data.etype:
            return
        await self.add_sibling(
            f"{etype.name}",
            generate_empty_entry(self.id + 1, entry.parent_id, etype.value),
        )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        entry.clear_content()

    def delete_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._action = Action.DELETE
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.clear_content()
        hl = config.styles["LOGGER_HIGHLIGHT"]
        ialogger.update(
            "[b]Delete[/]\n"
            + f"Type [{hl}]'delete'[/] and press [{hl}]enter[/]"
        )

    def rename_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._action = Action.RENAME
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.content = entry.name
        ialogger.update(f"[b]Rename[/]\nType new name")

    def move_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._action = Action.MOVE
        self._selected = self.nodes[self.cursor].id
        self._tree.hide_root = False
        self.refresh(layout=True)
        ialogger.update("Select new parent")

    def reset_entry_time(self, recursively: bool = False) -> None:
        if not self._valid_cursor():
            return

        entry = self.nodes[self.cursor].data
        if recursively:
            self._action = Action.RESET_REC
        elif entry.etype is EntryType.FOLDER:
            ialogger.update("Can't reset folder time", error=True)
            return
        else:
            self._action = Action.RESET
        self._mode = Mode.INSERT
        entry.clear_content()
        hl = config.styles["LOGGER_HIGHLIGHT"]
        res = "Reset recursively" if recursively else "Reset"
        ialogger.update(
            f"[b]{res}[/]\n"
            + f"Type [{hl}]'reset'[/] and press [{hl}]enter[/]"
        )

    def _valid_cursor(self) -> bool:
        return self.cursor not in [self.root.id, self.root.children[0].id]

    def _collect_task_ids(self, node: TreeNode | None = None) -> list[int]:
        node = node if node else self.nodes[self.cursor]
        ids = [node.data.task_id]
        self._collect_children_ids(node, ids)
        return ids

    def _collect_children_ids(self, node: TreeNode, ids: list[int]) -> None:
        for nd in node.children:
            ids.append(nd.data.task_id)
            self._collect_children_ids(nd, ids)

    def add_time(self, seconds: int, node: TreeNode | None = None) -> None:
        node = node if node else self.nodes[self.cursor]
        node.data.own_time = self.sum_time(node.data.own_time, (seconds,) * 3)
        self.sum_time_recursively()

    def _reset_time_recursively(self, node: TreeNode | None = None) -> None:
        node = node if node else self.nodes[self.cursor]
        node.data.reset_own_time()
        for nd in node.children:
            self._reset_time_recursively(nd)

    async def toggle_all_entries_recursively(self) -> None:
        if len(self.root.children) > 1:
            for node in self.root.children:
                await self.toggle_folding_recursively(
                    node, not self.root.children[-1].expanded
                )

    def render(self) -> RenderableType:
        return Panel(self._tree, border_style=config.styles["TASKLIST_BORDER"])

    def render_node(self, node: TreeNode) -> RenderableType:
        if node is self.root:
            rendr = self._render_root()
        elif node is self.root.children[0]:
            rendr = self._render_header()
        else:
            rendr = self._render_entry(node)
        if node.id == self.cursor:
            rendr.row_styles = [config.styles["HIGHLIGHTED_TASK"]]
        elif node.id == self._selected:
            rendr.row_styles = [config.styles["SELECTED_ENTRY"]]
        return rendr

    def _render_entry(self, node: TreeNode) -> Table:

        grid = Table.grid(expand=True)
        grid.add_row(
            self._render_name(node),
            self._render_time(node.data.time),
        )
        return grid

    def _render_name(self, node: TreeNode) -> RenderableType:
        cursor = self.cursor == node.id and self._mode is Mode.INSERT
        name = node.data._render_with_cursor() if cursor else node.data.name
        if node.data.etype is EntryType.FOLDER:
            name = f"🗁  {name}" if node.expanded else f"🗀 {name}"
        return name

    def _render_time(self, time: TimeTuple) -> RenderableType:
        time_str = map(sec_to_str, time)
        return Text.assemble(
            *map(lambda x: x.ljust(12, " "), time_str),
            justify="right",
        )

    def _render_header(self) -> Table:
        text_data = (
            "Today".rjust(12, " ")
            + "Month".rjust(12, " ")
            + "Total".rjust(12, " ")
        )

        name = Text("Projects", justify="left")
        time = Text(text_data, justify="right")

        header = Table.grid(expand=True)
        header.add_row(name, time)
        header.row_styles = [config.styles["TASKLIST_HEADER"]]
        return header

    def _render_root(self) -> Table:
        grid = Table.grid()
        grid.add_row(self.root.label)
        return grid
