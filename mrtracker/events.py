from textual.events import Event


class DbUpdate(Event, bubble=True):
    pass
