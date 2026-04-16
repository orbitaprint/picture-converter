
class FileQueueModel(object):
    def __init__(self, allow_duplicates=False):
        self._items = []
        self.allow_duplicates = allow_duplicates

    def items(self):
        return list(self._items)

    def add(self, path):
        if (not self.allow_duplicates) and path in self._items:
            return False
        self._items.append(path)
        return True

    def clear(self):
        self._items = []

    def remove_indexes(self, indexes):
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self._items):
                del self._items[idx]

    def move_up(self, index):
        if index <= 0 or index >= len(self._items):
            return index
        self._items[index - 1], self._items[index] = self._items[index], self._items[index - 1]
        return index - 1

    def move_down(self, index):
        if index < 0 or index >= len(self._items) - 1:
            return index
        self._items[index + 1], self._items[index] = self._items[index], self._items[index + 1]
        return index + 1

    def __len__(self):
        return len(self._items)
