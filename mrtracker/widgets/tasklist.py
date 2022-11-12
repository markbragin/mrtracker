from sqlite3 import IntegrityError

from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.reactive import Reactive, events
from textual.widgets import NodeID, TreeNode

from ..db import Database
from ..config import config
from ..events import DbUpdate
from ..mode import Action, Mode
from ..stopwatch import sec_to_str
from .entry import Entry, generate_entry
from .in_app_logger import ialogger
from .nested_list import NestedList

db = Database()


HL = config.styles["LOGGER_HIGHLIGHT"]

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
    _selected: Reactive[NodeID | None] = Reactive(None)
    _mode: Reactive[Mode] = Reactive(Mode.NORMAL)
    _action: Action | None = None
    _mem: NodeID = NodeID(0)
    _show_tags: Reactive[bool] = Reactive(False)
    _list_style: Reactive[int] = Reactive(config.styles["DEFAULT_FORMAT"])

    def __init__(
        self,
        label: TextType = "root",
        data=None,
        name: str | None = None,
        padding: PaddingDimensions = 0,
    ) -> None:
        super().__init__(label=label, data=data, name=name, padding=padding)
        self._tree.hide_root = True

    async def on_mount(self) -> None:
        await self.collect_data()

    async def collect_data(self) -> None:
        self._projects = db.fetch_projects()
        self._tasks = db.fetch_tasks()
        await self.add_header()
        await self._build_tree()
        await self.root.expand()
        self.sum_projects_time()

    async def add_header(self) -> None:
        self.id = -2
        await self.add(NodeID(0), "header", None)
        self.id = 0

    async def _build_tree(self) -> None:
        for row in self._projects:
            self.id = row[0] - 1
            await self.add(NodeID(0), row[1], Entry(row))

        for row in self._tasks:
            await self.add(row[1], row[2], Entry(row))

    def sum_projects_time(self) -> None:
        for project in self.root.children[1:]:
            project.data.time = sum(
                task.data.time for task in project.children
            )

    async def on_focus(self) -> None:
        self._mode = Mode.NORMAL

    async def on_key(self, event: events.Key) -> None:
        if self._mode is Mode.NORMAL:
            await self._handle_keypress_in_normal_mode(event)
        elif self._mode is Mode.INSERT:
            await self._handle_keypress_in_insert_mode(event)

    async def _handle_keypress_in_normal_mode(self, event: events.Key) -> None:
        key = event.key.translate(cyrillic_layout)
        if event.key == "escape":
            await self._cancel()
        elif event.key == "enter":
            if self._action == Action.MOVE:
                await self._handle_moving_entry()
            else:
                self._handle_starting_task()
        elif key in [config.tasklist_keys["go_down"], "down"]:
            await self.go_down()
        elif key in [config.tasklist_keys["go_up"], "up"]:
            await self.go_up()
        elif key == config.tasklist_keys["add_task"]:
            await self.add_task()
        elif key == config.tasklist_keys["new_project"]:
            await self.add_project()
        elif key == config.tasklist_keys["rename_entry"]:
            self.rename_entry()
        elif key == config.tasklist_keys["delete_entry"]:
            self.delete_entry()
        elif key == config.tasklist_keys["reset_entry_time"]:
            self.reset_entry_time()
        elif key == config.tasklist_keys["move_entry"]:
            self.move_entry()
        elif key == config.tasklist_keys["change_tag"]:
            self.change_tag()
        elif key == config.tasklist_keys["show_tags"]:
            self.toggle_tags()
        elif key == config.tasklist_keys["toggle_project"]:
            await self.toggle_project()
        elif key == config.tasklist_keys["toggle_all_projects"]:
            await self.toggle_all_projects()
        elif key in ["1", "2", "3"]:
            self._list_style = int(key)

    async def _cancel(self) -> None:
        if not self._action:
            return
        elif self._action is Action.ADD:
            await self.remove_node()
        ialogger.update("Canceled")
        self._action = None
        self._selected = None
        self._mode = Mode.NORMAL
        self.cursor = self._mem

    async def _handle_moving_entry(self) -> None:
        selected = self.nodes[self._selected]
        curr = self.nodes[self.cursor]
        if selected.parent is curr.parent:
            self._swap_entries()
        elif selected.data.type == "task" and curr.data.type == "project":
            self._change_project()
        else:
            ialogger.update(
                f"Can't swap [{HL}]{selected.data.title}[/] ⮀ "
                f"[{HL}]{curr.data.title}[/]",
                error=True,
            )
            return
        self.cursor = self._selected if self._selected else self.cursor
        self._selected = None
        self._action = None
        await self.app.post_message_from_child(DbUpdate(self))
        ialogger.update("[b]DONE[/]")

    def _swap_entries(self) -> None:
        one = self.nodes[self._selected]
        two = self.nodes[self.cursor]
        self._swap_entry_ids(one.data, two.data)
        self._swap_trees(one, two)
        self._swap_nodes(one, two)
        if one.data.type == "task":
            db.swap_tasks(one.data.id, two.data.id)
        else:
            db.swap_projects(one.data.id, two.data.id)

    def _swap_entry_ids(self, one: Entry, two: Entry) -> None:
        one.id, two.id = two.id, one.id

    def _swap_nodes(self, one: TreeNode, two: TreeNode) -> None:
        children = one.parent.children
        idx1 = children.index(one)
        idx2 = children.index(two)
        children[idx1], children[idx2] = children[idx2], children[idx1]

    def _swap_trees(self, one: TreeNode, two: TreeNode) -> None:
        children = one.parent.tree.children
        idx1 = children.index(one.tree)
        idx2 = children.index(two.tree)
        children[idx1], children[idx2] = children[idx2], children[idx1]

    def _change_project(self) -> None:
        selected_node = self.nodes[self._selected]
        curr_node = self.nodes[self.cursor]
        self._move_to_new_parent(selected_node, curr_node)
        selected_node.data.project_id = curr_node.data.id
        db.change_project(selected_node.data.id, curr_node.data.id)
        self.sum_projects_time()

    def _move_to_new_parent(self, node: TreeNode, new_par: TreeNode) -> None:
        new_par.tree.children.append(node.tree)
        node.parent.tree.children.remove(node.tree)

        new_par.children.append(node)
        node.parent.children.remove(node)

        node.parent = new_par
        node.data.parent_id = new_par.data.id

    def _handle_starting_task(self) -> None:
        if self.current_task:
            ialogger.update("[b]Timer is already running[/]", error=True)
        else:
            entry = self.nodes[self.cursor].data
            if entry.type == "project":
                ialogger.update("Select task, not project", error=True)
            else:
                self.current_task = entry

    async def go_down(self) -> None:
        await self.cursor_down()

    async def go_up(self) -> None:
        if self.nodes[self.cursor].previous_node is not self.root.children[0]:
            await self.cursor_up()

    async def add_task(self) -> None:
        if not self._valid_cursor():
            return
        node = self.nodes[self.cursor]
        self._mem = self.cursor
        if node.data.type == "project":
            await self.add_child(
                "task",
                generate_entry(db.get_next_task_id(), node.data.id),
            )
        else:
            await self.add_sibling(
                "task",
                generate_entry(db.get_next_task_id(), node.parent.data.id),
            )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        node.data.clear_content()

    async def add_project(self) -> None:
        self._mem = self.cursor
        await self.add_root_child(
            "project",
            generate_entry(db.get_next_project_id(), None),
        )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        self.nodes[self.cursor].data.clear_content()

    def rename_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._mem = self.cursor
        self._action = Action.RENAME
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.content = entry.title
        ialogger.update(f"[b]Rename[/]\nType new name")

    def delete_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._mem = self.cursor
        self._action = Action.DELETE
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.clear_content()
        ialogger.update(
            f"Type [{HL}]'delete'[/] to delete [{HL}]{entry.title}[/]"
        )

    def reset_entry_time(self) -> None:
        if not self._valid_cursor():
            return
        self._mem = self.cursor
        entry = self.nodes[self.cursor].data
        self._action = Action.RESET
        self._mode = Mode.INSERT
        entry.clear_content()
        ialogger.update(
            f"Type [{HL}]'reset'[/] to reset [{HL}]{entry.title}[/] time"
        )

    def move_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._mem = self.cursor
        self._action = Action.MOVE
        self._selected = self.nodes[self.cursor].id
        ialogger.update("Select target")

    def change_tag(self) -> None:
        if not self._valid_cursor():
            return
        self._mem = self.cursor
        self._action = Action.ADD_TAG
        self._mode = Mode.INSERT
        self.nodes[self.cursor].data.clear_content()
        ialogger.update("Type new tag")

    def toggle_tags(self) -> None:
        self._show_tags = not self._show_tags

    def _valid_cursor(self) -> bool:
        return self.cursor not in [self.root.id, self.root.children[0].id]

    async def toggle_project(self) -> None:
        if self.nodes[self.cursor].parent is not self.root:
            self._cur_to_parent()
        await self.nodes[self.cursor].toggle()

    async def toggle_all_projects(self) -> None:
        if not self._valid_cursor():
            return
        for project in self.root.children:
            await project.expand(not self.root.children[-1].expanded)
        if self.nodes[self.cursor].data.type == "task":
            self._cur_to_parent()

    async def _handle_keypress_in_insert_mode(self, event: events.Key) -> None:
        self.nodes[self.cursor].data.on_key(event)
        if event.key == "escape":
            await self._cancel()
        elif event.key == "enter":
            if self._action is Action.ADD:
                await self._handle_adding_entry()
            elif self._action is Action.RENAME:
                await self._handle_renaming_entry()
            elif self._action is Action.DELETE:
                await self._handle_deleting_entry()
            elif self._action is Action.RESET:
                await self._handle_resetting_task_time()
            elif self._action is Action.ADD_TAG:
                await self._handle_changing_tag()
            self._action = None
            self._mode = Mode.NORMAL
        event.stop()
        self.refresh()

    async def _handle_adding_entry(self) -> None:
        entry = self.nodes[self.cursor].data
        if entry.content == entry.title == "":
            await self._cancel()
            return

        entry.title = entry.content
        if entry.type == "project":
            try:
                db.add_project(entry.title)
            except IntegrityError:
                ialogger.update(
                    "[red]ERROR[/]. "
                    + f"Project with name {entry.title} already exists",
                    error=True,
                )
                await self.remove_node()

        else:
            db.add_task(entry.title, entry.project_id)

    async def _handle_renaming_entry(self) -> None:
        entry = self.nodes[self.cursor].data
        if not entry.content or entry.title == entry.content:
            await self._cancel()
            return

        entry.title = entry.content
        if entry.type == "project":
            db.rename_project(entry.id, entry.title)
        else:
            db.rename_task(entry.id, entry.title)
        ialogger.update("[b]DONE[/]")

    async def _handle_deleting_entry(self) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if entry.content != "delete":
            await self._cancel()
            return

        if entry.type == "project":
            db.delete_project(entry.id)
        else:
            db.delete_task(entry.id)
        await self.remove_node()
        await self.go_down()
        self.sum_projects_time()
        await self.app.post_message_from_child(DbUpdate(self))
        ialogger.update("[b]DONE[/]")

    async def _handle_resetting_task_time(self) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if entry.content != "reset":
            await self._cancel()
            return

        if entry.type == "project":
            db.delete_sessions_by_task_ids(
                [child.data.id for child in node.children]
            )
            for t in node.children:
                t.data.time = 0
        else:
            db.delete_sessions_by_task_ids([entry.id])
            entry.time = 0
        self.sum_projects_time()
        await self.app.post_message_from_child(DbUpdate(self))
        ialogger.update("[b]DONE[/]")

    async def _handle_changing_tag(self) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        new_tag = entry.content if entry.content else None
        task_ids = []
        if entry.type == "project":
            for task_node in node.children:
                task_node.data.tag = new_tag
                task_ids.append(task_node.data.id)
        else:
            entry.tag = new_tag
            task_ids.append(entry.id)
        db.update_tags(task_ids, new_tag)
        await self.app.post_message_from_child(DbUpdate(self))
        ialogger.update("[b]DONE[/]")

    def add_time(self, time: int) -> None:
        self.current_task.time += time
        self.sum_projects_time()

    def render(self) -> RenderableType:
        return Panel(self._tree, border_style=config.styles["TASKLIST_BORDER"])

    def render_node(self, node: TreeNode) -> RenderableType:
        if node is self.root:
            return self._render_root()
        elif node is self.root.children[0]:
            return self._render_header()
        else:
            rendr = self._render_entry(node)
        if node.id == self.cursor:
            rendr.row_styles = [config.styles["HIGHLIGHTED_ENTRY"]]
        elif node.id == self._selected:
            rendr.row_styles = [config.styles["SELECTED_ENTRY"]]
        elif node.data.type == "project":
            rendr.row_styles = [config.styles["PROJECT_STYLE"]]
        elif node.data.type == "task":
            rendr.row_styles = [config.styles["TASK_STYLE"]]
        return rendr

    def _render_root(self) -> RenderableType:
        return self.root.label

    def _render_header(self) -> RenderableType:
        style = config.styles["TASKLIST_HEADER"]
        if self._list_style == 3:
            header = Table.grid(expand=True)
            header.add_row("Projects", Text("Time", justify="right"))
            header.row_styles = [style]
        else:
            header = f"[{style}]Projects"
        return header

    def _render_entry(self, node: TreeNode) -> Table:
        grid = Table.grid(expand=True)
        name = self._render_name(node)
        time = self._render_time(node) if node.data.title else Text("")
        if self._list_style == 1:
            grid.add_row(Text.assemble(name, time))
        elif self._list_style == 2:
            grid.add_row(Text.assemble(time, name))
        else:
            grid.add_row(name, time)
        return grid

    def _render_name(self, node: TreeNode) -> Text:
        cursor = self.cursor == node.id and self._mode is Mode.INSERT
        name = node.data.title
        if node.data.type == "project":
            if node.expanded:
                name = f"⇣ {name}"
            else:
                name = f"→ {name}"
                if node.children:
                    name = f"{name} [{len(node.children)}]"
        elif self._show_tags:
            name = f"{name} #{node.data.tag if node.data.tag else ''}"
        name = Text(name)
        if cursor:
            name = node.data._render_with_cursor()
        return name

    def _render_time(self, node: TreeNode) -> Text:
        justify = "right" if self._list_style == 3 else "left"
        return Text(
            f" {sec_to_str(node.data.time)} ",
            justify=justify,
        )
