from rich.console import RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.reactive import Reactive, events
from textual.widgets import NodeID, TreeNode

from .. import db
from ..config import config
from ..events import Upd
from ..mode import Action, Mode
from ..stopwatch import sec_to_str
from .entry import Entry, generate_entry
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
    _selected: Reactive[NodeID | None] = Reactive(None)
    _mode: Reactive[Mode] = Reactive(Mode.NORMAL)
    _action: Action | None = None
    _mem: NodeID = NodeID(0)
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
        if event.key in ["escape", "enter"]:
            cancel = event.key == "escape"
            if self._action == Action.MOVE:
                await self._handle_moving_entry(cancel)
            elif event.key == "enter":
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
        elif key == config.tasklist_keys["toggle_project"]:
            await self.toggle_project()
        elif key == config.tasklist_keys["toggle_all_projects"]:
            await self.toggle_all_projects()
        elif key in ["1", "2", "3"]:
            self._list_style = int(key)

    async def _handle_moving_entry(self, cancel: bool) -> None:
        selected_node = self.nodes[self._selected]
        new_parent = self.nodes[self.cursor]
        hl = config.styles["LOGGER_HIGHLIGHT"]
        if cancel:
            ialogger.update("Canceled")
            self._selected = None
            return
        elif self.cursor == selected_node.parent.id:
            ialogger.update("Select ANOTHER project", error=True)
            return
        elif self.nodes[self.cursor].data.type == "project":
            ialogger.update(
                f"[{hl}]{selected_node.data.title}[/]: "
                + f"[{hl}]{selected_node.parent.data.title}[/] -> "
                + f"[{hl}]{new_parent.data.title}[/]"
            )
            self._move_to_new_parent(selected_node, new_parent)
            db.change_project(selected_node.data.id, new_parent.data.id)
            self.sum_projects_time()
        else:
            ialogger.update(
                f"Can't move [{hl}]{selected_node.label}[/] to "
                f"[{hl}]{new_parent.label}[/]",
                error=True,
            )
            return
        self._action = None
        self._selected = None
        self.refresh(layout=True)

    def _move_to_new_parent(self, node: TreeNode, new_par: TreeNode) -> None:
        new_par.tree.children.append(node.tree)
        node.parent.tree.children.remove(node.tree)

        new_par.children.append(node)
        node.parent.children.remove(node)

        node.parent = new_par
        node.data.parent_id = new_par.data.id

    def _handle_starting_task(self) -> None:
        if self.current_task:
            ialogger.update(
                "[b]Timer is running[/]. "
                "To start new task restart the timer first.",
                error=True,
            )
            return
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
        elif self._action is Action.MOVE:
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
        if not self._valid_cursor():
            return
        node = self.nodes[self.cursor]
        self._mem = self.cursor
        await self.add_root_child(
            "project",
            generate_entry(db.get_next_project_id(), None),
        )
        self._action = Action.ADD
        self._mode = Mode.INSERT
        node.data.clear_content()

    def rename_entry(self) -> None:
        if not self._valid_cursor():
            return
        self._action = Action.RENAME
        self._mode = Mode.INSERT
        entry = self.nodes[self.cursor].data
        entry.content = entry.title
        ialogger.update(f"[b]Rename[/]\nType new name")

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

    def reset_entry_time(self) -> None:
        if not self._valid_cursor():
            return

        entry = self.nodes[self.cursor].data
        self._action = Action.RESET
        self._mode = Mode.INSERT
        entry.clear_content()
        hl = config.styles["LOGGER_HIGHLIGHT"]
        if entry.type == "project":
            ialogger.update(
                "[b]Reset[/]\n"
                f"Type [{hl}]'reset'[/] and press [{hl}]enter[/] "
                f"to reset time OF ALL '[{hl}]{entry.title.upper()}[/]' TASKS"
            )
        else:
            ialogger.update(
                "[b]Reset[/]\n"
                f"Type [{hl}]'reset'[/] and press [{hl}]enter[/] "
                "to reset task time"
            )

    def move_entry(self) -> None:
        if not self._valid_cursor():
            return
        if self.nodes[self.cursor].data.type == "project":
            ialogger.update("Can't move project", error=True)
            return
        self._action = Action.MOVE
        self._selected = self.nodes[self.cursor].id
        ialogger.update("Select another project")

    def _valid_cursor(self) -> bool:
        return self.cursor not in [self.root.id, self.root.children[0].id]

    async def toggle_project(self) -> None:
        if self.nodes[self.cursor].parent is not self.root:
            self._cur_to_parent()
        await self.nodes[self.cursor].toggle()

    async def toggle_all_projects(self) -> None:
        for project in self.root.children:
            await project.expand(not self.root.children[-1].expanded)

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
                await self._handle_resetting_task_time(cancel)
            self._action = None
            self._mode = Mode.NORMAL
        event.stop()
        self.refresh()

    async def _handle_adding_entry(self, cancel: bool = False) -> None:
        entry = self.nodes[self.cursor].data
        if entry.content == entry.title == "" or cancel:
            ialogger.update("Canceled")
            await self.remove_node()
            self.cursor = self._mem
        else:
            entry.title = entry.content
            if entry.type == "project":
                db.add_project(entry.title)
            else:
                db.add_task(entry.title, entry.project_id)
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                f"{entry.type.capitalize()} [{hl}]{entry.title}[/] added."
            )

    def _handle_renaming_entry(self, cancel: bool = False) -> None:
        entry = self.nodes[self.cursor].data
        if any((cancel, not entry.content, entry.title == entry.content)):
            ialogger.update("Canceled")
            return
        else:
            ialogger.update(
                f"{entry.type.capitalize()} renamed: "
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.title}[/] -> "
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.content}[/]."
            )
            entry.title = entry.content
            if entry.type == "project":
                db.rename_project(entry.id, entry.title)
            else:
                db.rename_task(entry.id, entry.title)

    async def _handle_deleting_entry(self, cancel: bool = False) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if cancel:
            ialogger.update("Canceled")
        elif entry.content == "delete":
            if entry.type == "project":
                db.delete_project(entry.id)
            else:
                db.delete_task(entry.id)
            await self.remove_node()
            await self.go_down()
            self.sum_projects_time()
            await self.app.post_message_from_child(Upd(self))
            hl = config.styles["LOGGER_HIGHLIGHT"]
            ialogger.update(
                f"{type(entry).__name__} "
                + f"[{hl}]{entry.title}[/] has been removed."
            )
        else:
            ialogger.update("Canceled")

    async def _handle_resetting_task_time(self, cancel: bool = False) -> None:
        node = self.nodes[self.cursor]
        entry = node.data
        if cancel:
            ialogger.update("Canceled")
        elif entry.content == "reset":
            if entry.type == "project":
                db.delete_sessions_by_task_ids(
                    [t.data.id for t in node.children]
                )

                for t in node.children:
                    t.data.time = 0
            else:
                db.delete_sessions_by_task_ids([entry.id])
                entry.time = 0
            self.sum_projects_time()
            await self.app.post_message_from_child(Upd(self))
            ialogger.update(
                f"[{config.styles['LOGGER_HIGHLIGHT']}]{entry.title}[/] "
                "time has been reset"
            )
        else:
            ialogger.update("Canceled")

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
