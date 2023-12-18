import time

import inject

from pyspring import auto_config
from pyspring.decorators import Bean, FunctionNameBean
from pyspring.scope import Scope


@Bean()
class BeanExample:
    time: float

    def __init__(self):
        self.time = time.time()


@FunctionNameBean(scope=Scope.prototype)
def current_time() -> int:
    return int(time.time())


@Bean()
class CurrentTimeHolder:
    current_time: int = inject.attr("current_time")  # type: ignore

    current_time_bean: BeanExample = inject.attr(BeanExample)  # type: ignore

    def print_time(self):
        print(self.current_time)

    def print_bean(self):
        print(self.current_time_bean.time)


if __name__ == "__main__":
    auto_config(path="examples")

    current_time_holder = inject.instance(CurrentTimeHolder)
    print(current_time_holder)
    print(current_time_holder.current_time)
    print(current_time_holder.current_time_bean)
    current_time_holder.print_bean()

    current_time_holder.print_time()
