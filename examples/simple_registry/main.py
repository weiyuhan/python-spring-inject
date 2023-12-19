import inject

from examples.simple_registry.components import SimpleRegistry
from pyspring import auto_config

if __name__ == "__main__":
    auto_config(path="examples/simple_registry")

    simple_registry = inject.instance(SimpleRegistry)

    # print all values
    for key in simple_registry.get_keys():
        print("key:", key)
        print("\tvalue:", simple_registry.get(key).val)
        print("\tvalue:", simple_registry.get(key).val)
        print()
