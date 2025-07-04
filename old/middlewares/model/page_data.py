from typing import TypeVar, Collection, List

T = TypeVar("T")


class PageData:
    def __init__(
        self,
        total_count: int = 0,
        page_size: int = 1,
        page_index: int = 1,
        page_data: Collection[T] = None,
    ):
        self._total_count = total_count
        self._page_size = max(page_size, 1)
        self._page_index = max(page_index, 1)
        self._page_data = page_data if page_data is not None else []

    @property
    def total_count(self):
        return self._total_count

    @total_count.setter
    def total_count(self, total_count: int):
        self._total_count = total_count

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, page_size: int):
        self._page_size = max(page_size, 1)

    @property
    def page_index(self):
        return self._page_index

    @page_index.setter
    def page_index(self, page_index: int):
        self._page_index = max(page_index, 1)

    @property
    def page_data(self) -> List[T]:
        if isinstance(self._page_data, list):
            return self._page_data
        return list(self._page_data)

    @page_data.setter
    def page_data(self, page_data: Collection[T]):
        self._page_data = page_data

    @property
    def total_pages(self):
        return (
            self._total_count // self._page_size
            if self._total_count % self._page_size == 0
            else (self._total_count // self._page_size) + 1
        )

    # def is_empty(self):
    #     return not bool(self._page_data)
    #
    # def is_not_empty(self):
    #     return bool(self._page_data)
