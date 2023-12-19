import random

from pyspring.decorators import Component
from pyspring.factory_model import BaseFactory


class FactoryExampleComponent:
    def __init__(self, val: int) -> None:
        self.val = val

    def hello(self) -> None:
        print("hello world")


@Component()
class FactoryExampleComponentFactory(BaseFactory[FactoryExampleComponent]):
    def get(self) -> FactoryExampleComponent:
        random_val = random.randint(0, 100)
        return FactoryExampleComponent(val=random_val)
