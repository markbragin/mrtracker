from textual.reactive import events

from .text_input import TextInput


class Entry(TextInput):

    _id: int
    _project_id: int | None
    _title: str
    _time: int

    def __init__(self, data: tuple) -> None:
        super().__init__()
        self._id = data[0]
        self._project_id = data[1]
        self._title = data[2]
        self._time = data[3] if data[3] else 0

    def on_key(self, event: events.Key) -> None:
        super().on_key(event)

    @property
    def id(self) -> int:
        return self._id

    @property
    def project_id(self) -> int | None:
        return self._project_id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new_title: str) -> None:
        self._title = new_title

    @property
    def time(self) -> int:
        return self._time

    @time.setter
    def time(self, new_time: int) -> None:
        self._time = new_time if new_time >= 0 else self._time

    @property
    def type(self) -> str:
        return "task" if self._project_id else "project"


def generate_entry(entry_id: int, project_id: int | None) -> Entry:
    return Entry((entry_id, project_id, "", 0))
