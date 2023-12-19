import inject

from examples.simple_config.config_components import (
    ParserExampleComponent, ParserProviderExampleComponent)
from examples.simple_config.config_components_registry import \
    ConfigurableExampleComponentRegistry
from pyspring import auto_config

if __name__ == "__main__":
    auto_config(
        path="examples/simple_config",
        config_path="examples/simple_config/example.hocon.conf",
    )

    # load components by name
    first = inject.instance("first")
    second = inject.instance("second")
    third = inject.instance("third")

    # values are configured in example.hocon.conf
    print(first.val, second.val, third.val)  # type: ignore

    # load compoments by registry
    registry = inject.instance(ConfigurableExampleComponentRegistry)
    print(registry.get_keys())

    registry.get("first").hello()
    registry.get("first").hello()
    # singleton scope
    print(registry.get("first") is registry.get("first"))

    registry.get("second").hello()
    registry.get("second").hello()
    # prototype scope
    print(registry.get("second") is registry.get("second"))

    registry.get("third").hello()
    registry.get("third").hello()
    # singleton scope
    print(registry.get("third") is registry.get("third"))

    # parser example
    parser_product = inject.instance(ParserExampleComponent)
    print(parser_product.val)

    # parser provider example
    parser_provider_product = inject.instance(ParserProviderExampleComponent)
    print(parser_provider_product.val, parser_provider_product.current_time)
    print(parser_provider_product.factory_example_component)
    print(parser_provider_product.factory_example_component.val)
