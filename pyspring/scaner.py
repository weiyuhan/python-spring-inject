import importlib
import inspect
import os
import sys
from typing import Any, List, Optional, Tuple

from pyhocon import ConfigFactory, ConfigList, ConfigTree

from pyspring.decorators import (BeanData, ComponentData,
                                 ConfigurableComponentData, ConfigurationData,
                                 DecoratorData, DecoratorType)


def scan(
    folder_path: str,
) -> List[DecoratorData]:
    scan_results: List[Any] = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                module_path = file_path.replace("/", ".").replace("\\", ".")[:-3]
                module = importlib.import_module(module_path)
                for obj in inspect.getmembers(module, inspect.isclass):
                    cls = obj[1]
                    binding_type = getattr(cls, "__binding__", None)
                    if binding_type is None:
                        continue
                    if binding_type == DecoratorType.component:
                        scan_results.append(ComponentData.from_cls(cls))
                    if binding_type == DecoratorType.configuration:
                        result = ConfigurationData.from_cls(cls)
                        scan_results.append(result)
                        scan_results.extend(BeanData.from_configuration(cls))
                    if binding_type == DecoratorType.configurable_component:
                        scan_results.append(ConfigurableComponentData.from_cls(cls))
                for obj in inspect.getmembers(module, inspect.isfunction):
                    func = obj[1]
                    if getattr(func, "__binding__", None) == DecoratorType.bean:
                        scan_results.append(BeanData.from_func(func))
        for dir in dirs:
            scan_results.extend(scan(os.path.join(root, dir)))
    return scan_results


def split_configurable_component_scan_results(
    scan_results: List[DecoratorData],
) -> Tuple[List[ConfigurableComponentData], List[DecoratorData]]:
    configurable_component_scan_results: List[ConfigurableComponentData] = []
    other_scan_results = []
    for scan_result in scan_results:
        if scan_result.decorator_type == DecoratorType.configurable_component:
            assert isinstance(scan_result, ConfigurableComponentData)
            configurable_component_scan_results.append(scan_result)
        else:
            other_scan_results.append(scan_result)
    return configurable_component_scan_results, other_scan_results


def flatten_config_with_decorator_data(
    configurable_component_data_list: List[ConfigurableComponentData],
    config_paths: List[str],
) -> List[ConfigurableComponentData]:
    if not config_paths or not configurable_component_data_list:
        return configurable_component_data_list

    config_tree_list: List[ConfigTree] = []
    for config_path in config_paths:
        assert os.path.exists(config_path), f"{config_path} not exists"
        assert os.path.isfile(config_path), f"{config_path} is not a file"
        assert config_path.endswith(".conf"), f"{config_path} is not a conf file"
        config_tree_list.append(ConfigFactory.parse_file(config_path))

    result: List[ConfigurableComponentData] = []
    for configurable_component_data in configurable_component_data_list:
        for config_tree in config_tree_list:
            candidate_or_list: Optional[Any] = None
            if configurable_component_data.config_path is None:
                candidate_or_list = config_tree
            else:
                candidate_or_list = config_tree.get(
                    configurable_component_data.config_path, None
                )
            if candidate_or_list is None:
                continue

            config_or_list: Optional[Any] = None
            if type(candidate_or_list) == list or isinstance(
                candidate_or_list, ConfigList
            ):
                config_or_list = []
                for candidate in candidate_or_list:
                    if (
                        candidate.get("class", None)
                        in configurable_component_data.scan_cls_names
                    ):
                        config_or_list.append(candidate)
            elif (
                candidate_or_list.get("class", None)
                in configurable_component_data.scan_cls_names
            ):
                config_or_list = candidate_or_list
            else:
                config_or_list = None

            if config_or_list is not None:
                # if config is list
                if isinstance(config_or_list, list):
                    for config_item in config_or_list:
                        _configurable_component_data = (
                            configurable_component_data.copy()
                        )
                        _configurable_component_data.config = config_item
                        result.append(_configurable_component_data)
                else:
                    _configurable_component_data = configurable_component_data.copy()
                    _configurable_component_data.config = config_or_list
                    result.append(_configurable_component_data)
    return result


def auto_scan(
    path: Optional[str] = None,
    paths: Optional[List[str]] = None,
    config_path: Optional[str] = None,
    config_paths: Optional[List[str]] = None,
) -> List[DecoratorData]:
    _scan_paths = []
    if path:
        _scan_paths.append(path)
    if paths:
        _scan_paths.extend(paths)
    if not _scan_paths:
        # use sys.path
        _scan_paths = sys.path

    _config_paths = []
    if config_path:
        _config_paths.append(config_path)
    if config_paths:
        _config_paths.extend(config_paths)

    scan_results = []

    for _scan_path in _scan_paths:
        scan_results.extend(scan(_scan_path))

    (
        configurable_component_scan_results,
        other_scan_results,
    ) = split_configurable_component_scan_results(scan_results)

    flattened_configurable_components = flatten_config_with_decorator_data(
        configurable_component_scan_results, _config_paths
    )

    final_results: List[DecoratorData] = other_scan_results
    final_results.extend(flattened_configurable_components)
    return final_results
