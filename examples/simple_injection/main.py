import time

import inject

from examples.simple_injection.components import (CurrentTimeHolder,
                                                  OrdinaryObject)
from pyspring import auto_config

if __name__ == "__main__":
    auto_config(path="examples/simple_injection")

    current_time_holder = inject.instance(CurrentTimeHolder)

    # will get different time because of prototype scope
    current_time_holder.print_time_from_prototype()
    time.sleep(2)
    current_time_holder.print_time_from_prototype()

    # will get same time because of singleton scope
    current_time_holder.print_time_from_singleton()
    time.sleep(2)
    current_time_holder.print_time_from_singleton()

    # ordinary object can also be injected
    ordinary_object = OrdinaryObject()
    ordinary_object.print_time()

    # example for named_component
    named_component = inject.instance("named_component")
    named_component.hello()  # type: ignore
