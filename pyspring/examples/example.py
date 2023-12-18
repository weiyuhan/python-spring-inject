import random

from pyspring.decorators import Component, ConfigurableComponent


class BaseComponent:
    def hello(self) -> None:
        raise NotImplementedError()


@Component()
class ExampleComponent(BaseComponent):
    def hello(self) -> None:
        print(f"hello world from {self.__class__.__name__}")


@ConfigurableComponent()
class ConfigurableExampleComponent:
    val: int
    random_val: int

    def __init__(self, val: int) -> None:
        self.val = val
        self.random_val = random.randint(0, 100)

    def hello(self) -> None:
        print(
            f"hello world from configurable component {id(self)} with val: {self.val}"
            + f" and random val: {self.random_val}"
        )
