import inspect
from typing import Any, Dict, Type

from inject import (_BINDING_LOCK, Binding, Constructor, ConstructorTypeError,
                    Injectable, Injector, InjectorException, logger)


def match_cls(cls: Type[Any], cls_name: str) -> bool:
    if cls.__name__ == cls_name:
        return True
    for base_cls in cls.__bases__:
        if match_cls(base_cls, cls_name):
            return True
    return False


class EnhancementInjector(Injector):
    def bind_subclass(self, cls: Type[Any]) -> bool:
        new_bindings: Dict[Binding, Constructor] = {}
        for k, v in self._bindings.items():
            if inspect.isclass(k) and issubclass(k, cls) and k != cls:
                if cls in new_bindings and new_bindings[cls] != v:
                    raise InjectorException(
                        "Cannot create a runtime binding, multiple subclass bindings were found, key=%s"
                        % cls
                    )
                new_bindings[cls] = v

        if len(new_bindings) == 0:
            return False
        self._bindings.update(new_bindings)
        return True

    def bind_cls_by_name(self, cls_name: str) -> bool:
        new_bindings: Dict[Binding, Constructor] = {}
        for k, v in self._bindings.items():
            if inspect.isclass(k) and match_cls(k, cls_name):
                if cls_name in new_bindings and new_bindings[cls_name] != v:
                    raise InjectorException(
                        "Cannot create a runtime binding, multiple subclass bindings were found, key=%s"
                        % cls_name
                    )
                new_bindings[cls_name] = v

        if len(new_bindings) == 0:
            return False
        self._bindings.update(new_bindings)
        return True

    def get_instance(self, cls: Binding) -> Injectable:  # type: ignore
        """Return an instance for a class."""
        binding = self._bindings.get(cls)
        if binding:
            return binding()

        with _BINDING_LOCK:
            binding = self._bindings.get(str(cls))
            if binding:
                return binding()

            if not self._bind_in_runtime:
                raise InjectorException("No binding was found for key=%s" % cls)

            # check whether cls is str, and cls is a class name
            if isinstance(cls, str):
                _success = self.bind_cls_by_name(cls)
                if _success:
                    return self.get_instance(cls)

            if not callable(cls):
                raise InjectorException(
                    "Cannot create a runtime binding, the key is not callable, key=%s"
                    % cls
                )

            # check whether cls is type
            if inspect.isclass(cls):
                _success = self.bind_subclass(cls)
                if _success:
                    return self.get_instance(cls)

            try:
                instance = cls()
            except TypeError as previous_error:
                raise ConstructorTypeError(cls, previous_error)

            self._bindings[cls] = lambda: instance

            logger.debug(
                "Created a runtime binding for key=%s, instance=%s", cls, instance
            )
            return instance
