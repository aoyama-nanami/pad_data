from collections import UserDict
from typing import Any, Callable, Iterator, Mapping, MutableMapping, TypeVar
from typing import Union

K = TypeVar('K')
V = TypeVar('V')
MaybeCallable = Union[V, Callable[[], V]]

class LazyDict(MutableMapping[K, V]):
    def __init__(self, data: Mapping[K, MaybeCallable[V]]):
        self.data = dict(data)

    def __getitem__(self, key: K) -> V:
        obj = self.data[key]
        if callable(obj):
            obj = obj()
            self.data[key] = obj
        return obj

    def __setitem__(self, key: K, value: MaybeCallable[V]) -> None:
        self.data[key] = value

    def __delitem__(self, key: K) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
