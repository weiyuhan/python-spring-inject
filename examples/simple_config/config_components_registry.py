from examples.simple_config.config_components import \
    ConfigurableExampleComponent
from pyspring.decorators import Component
from pyspring.registry import InjectedRegistry


@Component()
class ConfigurableExampleComponentRegistry(
    InjectedRegistry[ConfigurableExampleComponent]
):
    pass
