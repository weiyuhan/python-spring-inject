import inject

from examples.simple_factory.factory_components import FactoryExampleComponent
from pyspring import auto_config

if __name__ == "__main__":
    auto_config(
        path="examples/simple_factory",
    )

    factory_product = inject.instance(FactoryExampleComponent)
    print(factory_product.val)
