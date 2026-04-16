
class NotificationCenter(object):
    """Simple in-app message bus for status line updates."""

    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def notify(self, message, level="info"):
        for callback in self._subscribers:
            callback(message, level)
