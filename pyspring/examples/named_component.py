from pyspring.decorators import Prototype


@Prototype(key="component1")
class NamedExampleComponent:
    def hello(self) -> None:
        print("hello world from named component")
