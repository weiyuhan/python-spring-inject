import random

import inject
from pyhocon import ConfigTree

from pyspring.decorators import ConfigurableComponent
from pyspring.examples.example import ConfigurableExampleComponent
from pyspring.factory_model import BaseParser, BaseParserProvider


class ParserExampleComponent:
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


class ParserProviderExampleComponent:
    val: int
    current_time: int

    factory_example_component: ConfigurableExampleComponent = inject.attr(...)  # type: ignore


@ConfigurableComponent()
class ParserExampleComponentParser(BaseParser[ParserExampleComponent]):
    def parse(self, config: ConfigTree) -> ParserExampleComponent:
        val = config.get_int("val")
        return ParserExampleComponent(val=val**2)


class ParserProviderExampleComponentParser(BaseParser[ParserProviderExampleComponent]):
    current_time: int

    def __init__(self, current_time: int) -> None:
        self.current_time = current_time

    def parse(self, config: ConfigTree) -> ParserProviderExampleComponent:
        val = config.get_int("val")
        ret = ParserProviderExampleComponent()
        ret.val = val**2
        ret.current_time = self.current_time
        return ret


@ConfigurableComponent()
class ParserProviderExampleComponentParserProvider(
    BaseParserProvider[ParserProviderExampleComponent]
):
    current_time: int = inject.attr("current_time")  # type: ignore

    def get(self) -> BaseParser[ParserProviderExampleComponent]:
        return ParserProviderExampleComponentParser(current_time=self.current_time)  # type: ignore
