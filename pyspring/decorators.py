import enum
import inspect
from typing import Any, Callable, List, Optional, Type

from pyhocon import ConfigTree

from pyspring.factory_model import (BaseFactory, BaseParser,
                                    BaseParserProvider, get_product_type)
from pyspring.scope import Scope


class DecoratorType(enum.Enum):
    component = "component"
    configuration = "configuration"
    bean = "bean"
    configurable_component = "configurable_component"


class DecoratorData:
    decorator_type: DecoratorType

    def __init__(self, decorator_type: DecoratorType):
        self.decorator_type = decorator_type

    def get_key(self) -> Any:
        raise NotImplementedError()

    def get_product_type(self) -> Type[Any]:
        raise NotImplementedError()

    def copy(self) -> "DecoratorData":
        raise NotImplementedError()


class ComponentData(DecoratorData):
    decorator_type: DecoratorType = DecoratorType.component
    cls: type
    product_cls: type
    scope: Scope
    key: Any

    def __init__(self, cls: type, product_cls: type, scope: Scope, key: Any):
        super().__init__(DecoratorType.component)
        self.cls = cls
        self.product_cls = product_cls
        self.scope = scope
        self.key = key

    def get_key(self) -> Any:
        return self.key

    def get_product_type(self) -> Type[Any]:
        return self.product_cls

    @staticmethod
    def from_cls(cls: type) -> "ComponentData":
        return getattr(cls, "__binding_data__")


class ConfigurationData(DecoratorData):
    decorator_type: DecoratorType = DecoratorType.configuration
    cls: type

    def __init__(self, cls: type):
        super().__init__(DecoratorType.configuration)
        self.cls = cls

    def get_key(self) -> Any:
        return self.cls

    def get_product_type(self) -> Type[Any]:
        return self.cls

    @staticmethod
    def from_cls(cls: type) -> "ConfigurationData":
        return ConfigurationData(
            cls=cls,
        )


class BeanData(DecoratorData):
    decorator_type: DecoratorType = DecoratorType.bean
    cls: Optional[type]
    product_cls: type
    func: Callable
    scope: Scope
    key: Any

    def __init__(
        self,
        func: Callable,
        product_cls: type,
        scope: Scope,
        key: Any,
        cls: Optional[type] = None,
    ):
        super().__init__(DecoratorType.bean)
        self.func = func
        self.product_cls = product_cls
        self.scope = scope
        self.key = key
        self.cls = cls

    def get_key(self) -> Any:
        return self.key

    def get_product_type(self) -> Type[Any]:
        return self.product_cls

    @staticmethod
    def from_func(func: type) -> "BeanData":
        return getattr(func, "__binding_data__")

    @staticmethod
    def from_configuration(configuration: type) -> List["BeanData"]:
        scan_results: List[BeanData] = []
        for obj in inspect.getmembers(configuration, inspect.isfunction):
            func = obj[1]
            if getattr(func, "__binding__", None) == DecoratorType.bean:
                result = BeanData.from_func(func)
                result.cls = configuration
                scan_results.append(result)
        return scan_results


class ConfigurableComponentData(DecoratorData):
    decorator_type: DecoratorType = DecoratorType.configurable_component
    cls: type
    product_cls: type
    scan_cls_names: List[str] = []
    scope: Optional[Scope]
    config_path: Optional[str]
    config: Optional[ConfigTree]

    def __init__(
        self,
        cls: type,
        product_cls: type,
        scan_cls_names: List[str],
        scope: Optional[Scope] = None,
        config_path: Optional[str] = None,
        config: Optional[ConfigTree] = None,
    ):
        super().__init__(DecoratorType.configurable_component)
        self.cls = cls
        self.product_cls = product_cls
        self.scan_cls_names = scan_cls_names
        self.scope = scope
        self.config_path = config_path
        self.config = config

    def copy(self) -> "ConfigurableComponentData":
        return ConfigurableComponentData(
            cls=self.cls,
            product_cls=self.product_cls,
            scan_cls_names=self.scan_cls_names,
            scope=self.scope,
            config_path=self.config_path,
            config=self.config,
        )

    def get_key(self) -> Any:
        assert self.config is not None
        return self.config.get("key", None) or self.product_cls

    def get_product_type(self) -> Type[Any]:
        return self.product_cls

    def get_scope(self) -> Scope:
        assert self.config is not None
        _scope_str = self.config.get("scope", None)
        if _scope_str is not None:
            return Scope[_scope_str]
        else:
            return self.scope or Scope.singleton

    @staticmethod
    def from_cls(cls: type) -> "ConfigurableComponentData":
        return getattr(cls, "__binding_data__")


def ConfigurableComponent(
    scope: Optional[Scope] = None,
    config_path: Optional[str] = None,
) -> Callable[[Type], Type]:
    def wrapper(cls: type):
        if (
            issubclass(cls, BaseParser)
            or issubclass(cls, BaseParserProvider)
            or issubclass(cls, BaseFactory)
        ):
            product_cls = get_product_type(cls)
            assert product_cls is not None, "product_cls is None"
            scan_cls_names = [
                cls.__name__,
                product_cls.__name__,
                f"{cls.__module__}.{cls.__name__}",
                f"{product_cls.__module__}.{product_cls.__name__}",
            ]
        else:
            product_cls = cls
            scan_cls_names = [
                cls.__name__,
                f"{cls.__module__}.{cls.__name__}",
            ]
        data = ConfigurableComponentData(
            cls=cls,
            product_cls=product_cls,
            scan_cls_names=scan_cls_names,
            scope=scope,
            config_path=config_path,
        )
        setattr(cls, "__binding__", DecoratorType.configurable_component)
        setattr(cls, "__binding_data__", data)
        return cls

    return wrapper


def Component(
    key: Optional[Any] = None,
    scope: Scope = Scope.singleton,
) -> Callable[[Type], Type]:
    def wrapper(cls: type):
        if issubclass(cls, BaseFactory):
            product_cls = get_product_type(cls)
            assert product_cls is not None, f"product_cls is None for {cls}"
        else:
            product_cls = cls

        _key: Optional[Any] = None
        if key is not None:
            _key = key
        else:
            _key = product_cls

        data = ComponentData(
            cls=cls,
            product_cls=product_cls,
            scope=scope,
            key=_key,
        )
        setattr(cls, "__binding__", DecoratorType.component)
        setattr(cls, "__binding_data__", data)
        return cls

    return wrapper


def Prototype(
    key: Optional[Any] = None,
) -> Callable[[Type], Type]:
    return Component(key=key, scope=Scope.prototype)


def Singleton(
    key: Optional[Any] = None,
) -> Callable[[Type], Type]:
    return Component(key=key, scope=Scope.singleton)


def Configuration() -> Callable[[Type], Type]:
    def wrapper(cls: type):
        data = ConfigurationData(
            cls=cls,
        )
        setattr(cls, "__binding__", DecoratorType.configuration)
        setattr(cls, "__binding_data__", data)
        return cls

    return wrapper


def Bean(
    key: Optional[Any] = None,
    scope: Scope = Scope.singleton,
    use_func_name_as_key: bool = False,
) -> Callable[..., Any]:
    def wrapper(func: Callable[..., Any]):
        product_cls = inspect.signature(func).return_annotation
        if not key:
            if use_func_name_as_key:
                _key = func.__name__
            else:
                _key = product_cls
        else:
            _key = key
        data = BeanData(
            func=func,
            product_cls=product_cls,
            scope=scope,
            key=_key,
        )
        setattr(func, "__binding__", DecoratorType.bean)
        setattr(func, "__binding_data__", data)
        return func

    return wrapper


def FunctionNameBean(
    scope: Scope = Scope.singleton,
) -> Callable[..., Any]:
    return Bean(scope=scope, use_func_name_as_key=True)
