from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar, Union

from pyhocon import ConfigTree

T = TypeVar("T")


class BaseFactory(ABC, Generic[T]):
    @abstractmethod
    def get(self) -> T:
        pass


class BaseParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, config: ConfigTree) -> Union[T, BaseFactory[T]]:
        pass


class BaseParserProvider(ABC, Generic[T]):
    @abstractmethod
    def get(self) -> BaseParser[T]:
        pass


def get_product_type(
    base_type: Union[
        Type[BaseFactory[T]], Type[BaseParser[T]], Type[BaseParserProvider[T]]
    ],
) -> Optional[Type[T]]:
    # 获取父类的泛型参数类型
    parent_generic_type = None
    if not hasattr(base_type, "__orig_bases__"):
        return parent_generic_type
    for base in base_type.__orig_bases__:
        if hasattr(base, "__args__"):
            parent_generic_type = base.__args__[0]
            break
    return parent_generic_type
