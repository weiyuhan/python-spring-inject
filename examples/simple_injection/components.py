import time

import inject

from pyspring.decorators import Bean, Component, FunctionNameBean, Prototype
from pyspring.scope import Scope


@Prototype(key="named_component")
class NamedExampleComponent:
    def hello(self) -> None:
        print("hello world from named component")


@Component()
class SimpleComponent:
    time: float

    def __init__(self):
        self.time = time.time()


@FunctionNameBean(scope=Scope.prototype)
def current_time() -> int:
    return int(time.time())


@Bean()
class CurrentTimeHolder:
    current_time: int = inject.attr("current_time")  # type: ignore

    simple_component: SimpleComponent = inject.attr(SimpleComponent)  # type: ignore

    def print_time_from_prototype(self):
        print(self.current_time)

    def print_time_from_singleton(self):
        print(self.simple_component.time)


class OrdinaryObject:
    current_time: int = inject.attr("current_time")  # type: ignore

    def __init__(self):
        pass

    def print_time(self):
        print(self.current_time)
