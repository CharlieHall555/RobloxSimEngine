from __future__ import annotations

from typing import List, Optional, Dict , TYPE_CHECKING

if TYPE_CHECKING:
    from classes.roblox_classes.instance import Instance


class ChildrenList:

    def __init__(self) -> None:
        self._children: List[Instance] = []
        self._index: Dict[str, List[Instance]] = {}

    def on_name_change(self, instance: Instance, new_name: str) -> None:
        old_name = getattr(instance, "name", None)
        if old_name in self._index:
            bucket = self._index[old_name]
            if instance in bucket:
                bucket.remove(instance)
                if not bucket:
                    del self._index[old_name]
        instance.name = new_name
        bucket = self._index.setdefault(new_name, [])
        bucket.append(instance)

    def add_child(self, instance: Instance) -> None:
        name = getattr(instance, "name", None)
        self._children.append(instance)

        # Update index for fast lookup
        if name is not None:
            bucket = self._index.setdefault(name, [])
            bucket.append(instance)

    def remove_child(self, instance: Instance) -> None:
        if instance in self._children:
            self._children.remove(instance)
            name = getattr(instance, "name", None)
            if name in self._index:
                bucket = self._index[name]
                if instance in bucket:
                    bucket.remove(instance)
                    if not bucket:
                        del self._index[name]

    def get_child(self, name: str) -> Optional[Instance]:
        bucket = self._index.get(name)
        return bucket[0] if bucket else None

    def all(self) -> List[Instance]:
        return list(self._children)

    def contains(self, child_name: str) -> bool:
        return child_name in self._index and bool(self._index[child_name])