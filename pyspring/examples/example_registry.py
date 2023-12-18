from pyspring.decorators import Component
from pyspring.examples.example import ConfigurableExampleComponent
from pyspring.registry import InjectedRegistry


@Component()
class ConfigurableExampleComponentRegistry(
    InjectedRegistry[ConfigurableExampleComponent]
):
    pass
