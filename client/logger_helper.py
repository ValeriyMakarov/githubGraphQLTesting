import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any

import allure


def log_all_methods(cls):
    cls.logger = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    for attr_name, attr_value in cls.__dict__.items():
        is_method = (
            inspect.isfunction(attr_value)
            or isinstance(attr_value, (staticmethod, classmethod))
        )
        has_valid_name = not attr_name.startswith("_")

        if is_method and isinstance(attr_value, staticmethod) and has_valid_name:
            func = attr_value.__func__
            setattr(cls, attr_name, staticmethod(_log_method(func)))
        elif is_method and has_valid_name:
            setattr(cls, attr_name, _log_method(attr_value))

    return cls


def log_function(func):
    """
    Logging decorator for functions.
    """
    logger = logging.getLogger(func.__module__)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name, parameters = _get_func_data(func, *args, **kwargs)
        name = _format_func_name(name)
        filtered_parameters = _filter_parameters(parameters)

        step_name = _compile_step_name(name, filtered_parameters)
        with allure.step(step_name):
            logger.info(step_name)
            result = func(*args, **kwargs)
        return result

    return wrapper


def _log_method(func):
    """
    Logging decorator for methods.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name, parameters = _get_func_data(func, *args, **kwargs)
        name = _format_func_name(name)
        has_self_or_cls_as_first_arg = bool(parameters) and parameters[0][0] in ("cls", "self")
        filtered_parameters = _filter_parameters(parameters)

        step_name = _compile_step_name(name, filtered_parameters)
        with allure.step(step_name):
            if has_self_or_cls_as_first_arg:
                parameters[0][1].logger.info(step_name)
            result = func(*args, **kwargs)
        return result
    return wrapper


def _format_func_name(name: str):
    """
    Formats function name from "_function_name" to "Function name"
    :param name: function name.
    :return: formatted function name.
    """
    return f'{name.replace("_", " ").strip().capitalize()}'


def _compile_step_name(base_name: str, parameters: list[tuple[str, Any]]):
    def wrap(item):
        return f'"{item}"' if isinstance(item, str) else item

    additional_data = ', '.join(f'{name}={wrap(value)}' for name, value in parameters)
    return f'{base_name} with {additional_data}.' if additional_data else f'{base_name}.'


def _get_func_data(func: Callable, *args, **kwargs) -> tuple[str, list[tuple[str, Any]]]:
    func_signature = inspect.signature(func)
    func_data: inspect.BoundArguments = func_signature.bind_partial(*args, **kwargs)
    func_data.apply_defaults()

    parameters = list(func_data.arguments.items()) + list(func_data.kwargs.items())

    return func.__name__, parameters


def _filter_parameters(parameters: list[tuple[str, Any]]):
    def is_scalar(item):
        return isinstance(item, (int, float, str, bool, type(None)))

    return [item for item in parameters if is_scalar(item[1])]
