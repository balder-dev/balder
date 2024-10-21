from __future__ import annotations
from typing import Iterable, Any

import inspect
from _balder.collector import Collector


def parametrize(
        field_name: str,
        values: Iterable[Any],
):
    """
    Allows to parametrize a test function. This decorator will be used to statically parametrize a test function.

    :param field_name: the field name of the test function

    :param values: an iterable of values, that should be used to parametrize the test function
    """
    if not isinstance(field_name, str):
        raise ValueError('the given field name must be a string')

    def decorator(func):
        nonlocal field_name
        nonlocal values

        if not inspect.isfunction(func):
            raise TypeError('the decorated object needs to be a test method')

        Collector.register_possible_parametrization(func, field_name, values)
        return func
    return decorator
