import time

import inject

from pyspring.decorators import Bean, Configuration, FunctionNameBean
from pyspring.scope import Scope


@Bean()
class BeanExample:
    time: float

    def __init__(self):
        self.time = time.time()


@Bean()
class CurrentTimeHolder:
    current_time: int = inject.attr("current_time")  # type: ignore

    current_time_bean: BeanExample = inject.attr(BeanExample)  # type: ignore

    def print_time(self):
        print(self.current_time)

    def print_bean(self):
        print(self.current_time_bean.time)


@FunctionNameBean(scope=Scope.prototype)
def current_time() -> int:
    return int(time.time())


@Configuration()
class ExampleConfiguration:
    @Bean(use_func_name_as_key=True)
    def bean(self) -> str:
        return "hello world from bean"
