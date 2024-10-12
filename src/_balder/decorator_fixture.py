from __future__ import annotations
from typing import Literal

import functools
from _balder.collector import Collector
from _balder.fixture_execution_level import FixtureExecutionLevel


def fixture(level: Literal['session', 'setup', 'scenario', 'variation', 'testcase']):
    """
    This decorator declares the decorated function/method as a fixture function/method.

    :param level: the execution level the fixture should have
    """
    allowed_levels = [level.value for level in FixtureExecutionLevel]

    if level not in allowed_levels:
        raise ValueError(f"the value of `level` must be a `str` with one of the values `{'`, `'.join(allowed_levels)}`")

    def decorator_fixture(func):
        # always register the raw fixture in Collector - class determination will be done later by :meth:`Collector`
        Collector.register_raw_fixture(func, level)

        @functools.wraps(func)
        def wrapper_fixture(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper_fixture
    return decorator_fixture
