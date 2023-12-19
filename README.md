# PySpring Dependency Injection Framework

PySpring is a lightweight dependency injection framework for Python that allows you to easily manage dependencies and configure your application's components. It provides some spring-like features such as auto-configuration and bean discovery:
- A simple API for defining beans and injecting dependencies into them.
- An auto-configuration feature that automatically discovers beans in specified paths and wires them together.
- Config beans in configuration files, now only support HOCON format. Check the [HOCON](https://github.com/lightbend/config/blob/main/HOCON.md) and [pyhocon](https://github.com/chimpler/pyhocon) for more details.

## Installation

PySpring is based on the [inject](https://pypi.org/project/inject/) library, which is a dependency injection framework for Python. (Currently, PySpring only supports inject version 5.0.0.)

You can install PySpring using pip:

```shell
pip install pyspring
```

## Getting Started
To use PySpring, you need to follow these steps:

Define your beans: Beans are the components of your application that can be injected with dependencies. You can define beans by creating classes and decorating them with the @Bean() decorator.

Define bean dependencies: You can inject dependencies into beans using the inject.attr() function. This function takes the name of the dependency as an argument and returns the instance of the dependency.

Configure your application: PySpring provides an auto_config() function that automatically discovers beans in specified paths and wires them together. You need to call this function to configure your application.

Obtain bean instances: After configuring your application, you can obtain instances of beans using the inject.instance() function. This function takes the class name of the bean as an argument and returns an instance of that bean.

## Example
Here's an example that demonstrates the usage of PySpring:

```python
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
```

In this example, we define two beans: BeanExample and CurrentTimeHolder. BeanExample has a single attribute time, which is initialized with the current time. CurrentTimeHolder has two attributes, current_time and current_time_bean, which are injected with dependencies using the inject.attr() function.

We also define a function current_time() as a bean using the @FunctionNameBean decorator. This function returns the current time as an integer.

To configure the application, we call auto_config() and provide the path where our beans are located.

Finally, we obtain an instance of CurrentTimeHolder using inject.instance() and demonstrate accessing its attributes and calling its methods.

### Check the examples folder for more examples.

## Conclusion
PySpring simplifies dependency injection in Python by providing a lightweight framework for managing dependencies and configuring your application's components. It allows you to decouple your code and improve testability and modularity. Give PySpring a try and enjoy the benefits of dependency injection in your Python projects!