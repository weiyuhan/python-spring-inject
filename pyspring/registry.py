from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, Generic, List, Set, Type, TypeVar

import inject

V = TypeVar("V")


class BaseRegistry(ABC, Generic[V]):
    @abstractmethod
    def get_keys(self) -> List[Any]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, key: Any) -> V:
        raise NotImplementedError()


class BindingKeyMap:
    binding_key_map: Dict[Type[Any], Set[Any]] = defaultdict(set)

    def add(self, value_type: Type[Any], key: Any) -> None:
        self.binding_key_map[value_type].add(key)

    def get(self, value_type: Type[Any]) -> Set[Any]:
        result_keys = set()
        for vt, ks in self.binding_key_map.items():
            # check if value_type is subclass of vt and key_type is subclass of kt
            if issubclass(vt, value_type) or vt == value_type:
                result_keys.update(ks)
        return result_keys


class InjectedRegistry(BaseRegistry[V]):
    binding_key_map: BindingKeyMap = inject.attr(BindingKeyMap)

    @property
    def get_type(
        self,
    ) -> Type[Any]:
        self_type = type(self)
        if hasattr(self_type, "__orig_bases__"):
            for base in self_type.__orig_bases__:
                if hasattr(base, "__args__"):
                    value_type = base.__args__[0]
                    return value_type
        raise Exception("can not get types")

    def get_keys(self) -> List[Any]:
        value_type = self.get_type
        return list(self.binding_key_map.get(value_type))

    def get(self, key: Any) -> V:
        return inject.instance(key)  # type: ignore
