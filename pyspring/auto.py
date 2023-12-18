import inspect
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

import inject
from pyhocon import ConfigTree

from pyspring.decorators import (BeanData, ComponentData,
                                 ConfigurableComponentData, ConfigurationData,
                                 DecoratorData)
from pyspring.factory_model import BaseFactory, BaseParser, BaseParserProvider
from pyspring.registry import BindingKeyMap
from pyspring.scope import Scope


class AttrInstanceInjector:
    attr_key_map: Dict[str, Any]

    def __init__(self, config: ConfigTree) -> None:
        self.attr_key_map = {}
        for attr_name in config.keys():
            attr_config = config.get(attr_name)
            if not isinstance(attr_config, ConfigTree):
                continue
            class_type = attr_config.get("class", None)
            if class_type not in (
                "pyspring.decorators.Component",
                "pyspring.decorators.Bean",
                "pyspring.decorators.Configuration",
                "Component",
                "Bean",
                "Configuration",
            ):
                continue

            _key = attr_config.get("key", None)
            if _key is None:
                raise Exception(f"attr_config {attr_config} is not configureed a key")
            self.attr_key_map[attr_name] = _key

    def __call__(self, instance: Any) -> Any:
        instance_attrs = set(dir(instance))
        for attr_name, key in self.attr_key_map.items():
            if attr_name not in instance_attrs:
                continue
            setattr(instance, attr_name, inject.instance(key))
        return instance


class Holder(ABC):
    attr_instance_injector: Optional[AttrInstanceInjector] = None

    @abstractmethod
    def get(self) -> Any:
        pass

    def inject_instance(self, instance: Any) -> Any:
        if self.attr_instance_injector is not None:
            return self.attr_instance_injector(instance)
        return instance


class InitFuncHolder(Holder):
    init_func: Callable[[], Any]
    args: List[Any]
    kwargs: Dict[str, Any]
    cls_key: Optional[Any] = None
    attr_instance_injector: Optional[AttrInstanceInjector] = None

    def __init__(
        self,
        init_func: Callable[[], Any],
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        cls_key: Optional[Any] = None,
        attr_instance_injector: Optional[AttrInstanceInjector] = None,
    ) -> None:
        self.init_func = init_func
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.cls_key = cls_key
        self.attr_instance_injector = attr_instance_injector


class SingletonHolder(InitFuncHolder):
    singleton: Any = None
    singleton_lock: threading.RLock = threading.RLock()

    def init_singleton(self) -> None:
        with self.singleton_lock:
            if self.singleton is None:
                if self.cls_key is not None:
                    cls_instance = inject.instance(self.cls_key)
                    _args = [cls_instance] + self.args
                    self.singleton = self.init_func(*_args, **self.kwargs)
                else:
                    self.singleton = self.init_func(*self.args, **self.kwargs)

    def get(self) -> Any:
        if self.singleton is None:
            self.init_singleton()
        if isinstance(self.singleton, BaseFactory):
            return self.inject_instance(self.singleton.get())
        return self.inject_instance(self.singleton)


class PrototypeHolder(InitFuncHolder):
    def get(self) -> Any:
        if self.cls_key is not None:
            cls_instance = inject.instance(self.cls_key)
            _args = [cls_instance] + self.args
            instance_or_factory = self.init_func(*_args, **self.kwargs)
        else:
            instance_or_factory = self.init_func(*self.args, **self.kwargs)
        instance_or_factory = self.inject_instance(instance_or_factory)
        if isinstance(instance_or_factory, BaseFactory):
            return self.inject_instance(instance_or_factory.get())
        return instance_or_factory


class ParserHolder(Holder):
    parser_cls: type
    config: ConfigTree
    scope: Scope

    parser_instance: Optional[BaseParser] = None
    singleton: Optional[Any] = None

    parser_lock: threading.RLock = threading.RLock()

    attr_instance_injector: Optional[AttrInstanceInjector] = None

    def __init__(
        self,
        parser_cls: type,
        config: ConfigTree,
        scope: Scope,
        attr_instance_injector: Optional[AttrInstanceInjector] = None,
    ) -> None:
        self.parser_cls = parser_cls
        self.config = config
        self.scope = scope
        self.attr_instance_injector = attr_instance_injector

    def init_parser(self) -> None:
        with self.parser_lock:
            if self.parser_instance is None:
                parser_or_provider = self.parser_cls()
                if isinstance(parser_or_provider, BaseParserProvider):
                    parser_or_provider = self.inject_instance(parser_or_provider)
                    self.parser_instance = self.inject_instance(
                        parser_or_provider.get()
                    )
                else:
                    self.parser_instance = parser_or_provider

    def init_singleton(self) -> None:
        with self.parser_lock:
            if self.singleton is None:
                if self.parser_instance is None:
                    self.init_parser()
                assert self.parser_instance is not None
                parser_instance = self.inject_instance(self.parser_instance)
                _singleton = parser_instance.parse(self.config)
                self.singleton = _singleton

    def get(self) -> Any:
        if self.parser_instance is None:
            self.init_parser()
        if self.scope == Scope.singleton:
            if self.singleton is None:
                self.init_singleton()
            if isinstance(self.singleton, BaseFactory):
                return self.inject_instance(self.singleton.get())
            return self.inject_instance(self.singleton)
        else:
            assert self.parser_instance is not None
            parser_instance = self.inject_instance(self.parser_instance)
            prototype = parser_instance.parse(self.config)
            if isinstance(prototype, BaseFactory):
                return self.inject_instance(prototype.get())
            return self.inject_instance(prototype)


class AutoBinder:
    decorator_data_list: List[DecoratorData]
    binder: Optional[inject.Binder] = None

    def __init__(self, decorator_data_list: List[DecoratorData]) -> None:
        self.decorator_data_list = decorator_data_list

    def auto_bind(self, binder: inject.Binder) -> None:
        self.binder = binder

        # deduplicate
        decorator_data_map: Dict[Any, DecoratorData] = {}
        for decorator_data in self.decorator_data_list:
            decorator_data_map[decorator_data.get_key()] = decorator_data

        binding_key_map = BindingKeyMap()

        for decorator_data in decorator_data_map.values():
            if isinstance(decorator_data, ComponentData):
                self.bind_component(decorator_data)
            if isinstance(decorator_data, ConfigurationData):
                self.bind_configuration(decorator_data)
            if isinstance(decorator_data, BeanData):
                self.bind_bean(decorator_data)
            if isinstance(decorator_data, ConfigurableComponentData):
                self.bind_configurable_component(decorator_data)

            key = decorator_data.get_key()
            product_type = decorator_data.get_product_type()
            binding_key_map.add(product_type, key)

        binder.bind(BindingKeyMap, binding_key_map)

    def bind_to_provider(self, cls: inject.Binding, provider: inject.Provider) -> None:
        assert self.binder is not None
        self.binder._check_class(cls)
        self.binder._bindings[cls] = provider

    def bind_component(self, component_data: ComponentData) -> None:
        assert self.binder is not None
        provider_func = component_data.cls

        if component_data.scope == Scope.singleton:
            singleton_holder = SingletonHolder(provider_func)
            self.bind_to_provider(component_data.get_key(), singleton_holder.get)
        else:
            prototype_holder = PrototypeHolder(provider_func)
            self.bind_to_provider(component_data.get_key(), prototype_holder.get)

    def bind_configuration(self, configuration_data: ConfigurationData) -> None:
        assert self.binder is not None
        self.binder.bind(configuration_data.get_key(), configuration_data.cls())

    def bind_bean(self, bean_data: BeanData) -> None:
        assert self.binder is not None
        if bean_data.scope == Scope.singleton:
            singleton_holder = SingletonHolder(bean_data.func, cls_key=bean_data.cls)
            self.bind_to_provider(bean_data.get_key(), singleton_holder.get)
        else:
            prototype_holder = PrototypeHolder(bean_data.func, cls_key=bean_data.cls)
            self.bind_to_provider(bean_data.get_key(), prototype_holder.get)

    def bind_configurable_component(
        self, configurable_component_data: ConfigurableComponentData
    ) -> None:
        assert self.binder is not None
        assert configurable_component_data.config is not None

        attr_instance_injector = None
        if configurable_component_data.config is not None:
            attr_instance_injector = AttrInstanceInjector(
                configurable_component_data.config,
            )
            if not attr_instance_injector.attr_key_map:
                attr_instance_injector = None

        _key = configurable_component_data.get_key()
        _scope = configurable_component_data.get_scope()
        if issubclass(
            configurable_component_data.cls, BaseParserProvider
        ) or issubclass(configurable_component_data.cls, BaseParser):
            parser_holder = ParserHolder(
                configurable_component_data.cls,
                configurable_component_data.config,
                _scope,
                attr_instance_injector=attr_instance_injector,
            )
            self.bind_to_provider(_key, parser_holder.get)
            return

        needed_kwargs = inspect.getfullargspec(configurable_component_data.cls).args
        candidate_kwargs = {}
        if configurable_component_data.config is not None:
            candidate_kwargs = (
                configurable_component_data.config.as_plain_ordered_dict()
            )
        kwargs = {}
        for needed_kwarg in needed_kwargs:
            if needed_kwarg == "self" or needed_kwarg not in candidate_kwargs:
                continue
            kwargs[needed_kwarg] = candidate_kwargs[needed_kwarg]

        if _scope == Scope.singleton:
            singleton_holder = SingletonHolder(
                configurable_component_data.cls,
                kwargs=kwargs,
                attr_instance_injector=attr_instance_injector,
            )
            self.bind_to_provider(_key, singleton_holder.get)
        else:
            prototype_holder = PrototypeHolder(
                configurable_component_data.cls,
                kwargs=kwargs,
                attr_instance_injector=attr_instance_injector,
            )
            self.bind_to_provider(_key, prototype_holder.get)
