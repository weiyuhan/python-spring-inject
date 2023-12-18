import inject

from pyspring import auto_config
from pyspring.examples.beans import CurrentTimeHolder
from pyspring.examples.example import BaseComponent, ExampleComponent
from pyspring.examples.example_registry import \
    ConfigurableExampleComponentRegistry
from pyspring.examples.factory_example import FactoryExampleComponent
from pyspring.examples.parser_example import (ParserExampleComponent,
                                              ParserProviderExampleComponent)

if __name__ == "__main__":
    auto_config(
        path="pyspring/examples", config_path="pyspring/examples/example.hocon.conf"
    )

    current_time_holder = inject.instance(CurrentTimeHolder)
    print(current_time_holder)
    print(current_time_holder.current_time)
    print(current_time_holder.current_time_bean)
    current_time_holder.print_bean()

    current_time_holder.print_time()

    example_component = inject.instance(ExampleComponent)
    example_component.hello()

    print(inject.instance("ExampleComponent"))
    print(inject.instance("BaseComponent"))

    base_component = inject.instance(BaseComponent)
    base_component.hello()
    print(base_component is example_component)

    component1 = inject.instance("component1")
    component2 = inject.instance("component1")
    print(component1 is component2)
    component1.hello()  # type: ignore

    current_time1 = inject.instance("current_time")
    current_time2 = inject.instance("current_time")
    print(current_time1, current_time2)

    first = inject.instance("first")
    second = inject.instance("second")
    third = inject.instance("third")

    print(first.val, second.val, third.val)  # type: ignore

    bean = inject.instance("bean")
    print(bean)

    registry = inject.instance(ConfigurableExampleComponentRegistry)
    print(registry.get_keys())
    registry.get("first").hello()
    registry.get("first").hello()
    print(registry.get("first") is registry.get("first"))

    registry.get("second").hello()
    registry.get("second").hello()
    print(registry.get("second") is registry.get("second"))

    registry.get("third").hello()
    registry.get("third").hello()
    print(registry.get("third") is registry.get("third"))

    factory_product = inject.instance(FactoryExampleComponent)
    print(factory_product.val)

    parser_product = inject.instance(ParserExampleComponent)
    print(parser_product.val)

    parser_provider_product = inject.instance(ParserProviderExampleComponent)
    print(parser_provider_product.val, parser_provider_product.current_time)
    print(parser_provider_product.factory_example_component)
    print(parser_provider_product.factory_example_component.val)

    print(inject.get_injector())
