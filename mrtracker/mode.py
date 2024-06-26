from enum import Enum, auto


class Mode(Enum):
    NORMAL = auto()
    INSERT = auto()


class Action(Enum):
    ADD = auto()
    RENAME = auto()
    DELETE = auto()
    RESET = auto()
    MOVE = auto()
    ADD_TAG = auto()
