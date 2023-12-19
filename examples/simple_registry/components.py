import random

from pyspring import Scope
from pyspring.decorators import Component, FunctionNameBean
from pyspring.registry import InjectedRegistry


@Component()
class SimpleComponent:
    val: int

    def __init__(self, val: int = 0):
        self.val = val


@FunctionNameBean()
def singleton_named_bean() -> SimpleComponent:
    return SimpleComponent(val=random.randint(0, 100))


@FunctionNameBean(scope=Scope.prototype)
def prototype_named_bean() -> SimpleComponent:
    return SimpleComponent(val=random.randint(0, 100))


@Component()
class SimpleRegistry(InjectedRegistry[SimpleComponent]):
    pass
