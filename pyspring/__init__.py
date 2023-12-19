from typing import List, Optional

import inject

from pyspring.auto import AutoBinder  # noqa: F401
from pyspring.decorators import Component  # noqa: F401
from pyspring.decorators import ConfigurableComponent  # noqa: F401
from pyspring.decorators import Configuration  # noqa: F401
from pyspring.decorators import Prototype  # noqa: F401
from pyspring.decorators import Bean, FunctionNameBean, Singleton  # noqa: F401
from pyspring.factory_model import BaseFactory  # noqa: F401
from pyspring.factory_model import BaseParser  # noqa: F401
from pyspring.factory_model import BaseParserProvider  # noqa: F401
from pyspring.injector import EnhancementInjector  # noqa: F401
from pyspring.registry import BaseRegistry, InjectedRegistry  # noqa: F401
from pyspring.scaner import auto_scan  # noqa: F401
from pyspring.scope import Scope  # noqa: F401


def auto_config(
    bind_in_runtime: bool = True,
    path: Optional[str] = None,
    paths: Optional[List[str]] = None,
    config_path: Optional[str] = None,
    config_paths: Optional[List[str]] = None,
) -> None:
    scan_results = auto_scan(path, paths, config_path, config_paths)
    auto_binder = AutoBinder(scan_results)

    with inject._INJECTOR_LOCK:
        inject._INJECTOR = EnhancementInjector(
            auto_binder.auto_bind, bind_in_runtime=bind_in_runtime
        )
