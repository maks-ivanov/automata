from abc import abstractmethod
from typing import Any


class BaseSelector:
    def __init__(self, item_iterable, num_items_to_show=10):
        self.item_iterable = item_iterable
        self.item_iterator = iter(self.item_iterable)
        self.num_items_to_show = num_items_to_show

    def list_items(self) -> str:
        # if iterator is empty, reset it
        if not self.item_iterator:
            self.item_iterator = iter(self.item_iterable)
        items = []
        for i in range(self.num_items_to_show):
            if not self.item_iterator:
                break
            index, item = next(self.item_iterator)
            items.append(f"{index}. {item}")
        return "\n".join(items)

    def select_and_process_item(self, index) -> Any:
        if index not in range(len(self.item_iterable)):
            raise ValueError(f"Index {index} not in coverage dataframe")
        return self.process_item(self.item_iterable[index][1])

    @abstractmethod
    def process_item(self, item) -> Any:
        """do something with the item"""