from __future__ import annotations
from typing import Literal

import functools
from _balder.collector import Collector
from _balder.fixture_manager import FixtureManager


def fixture(level: Literal['session', 'setup', 'scenario', 'variation', 'testcase']):
    """
    This decorator declares the decorated function/method as a fixture function/method.

    :param level: the execution level the fixture should have
    """
    allowed_levels = FixtureManager.EXECUTION_LEVEL_ORDER

    if level not in allowed_levels:
        raise ValueError(f"the value of `level` must be a `str` with one of the values `{'`, `'.join(allowed_levels)}`")

    def decorator_fixture(func):
        # always add the fixture to FixtureManager.raw_fixtures - class determination will be done later by
        # :meth:`Collector`
        if level not in Collector.raw_fixtures.keys():
            Collector.raw_fixtures[level] = []
        Collector.raw_fixtures[level].append(func)

        @functools.wraps(func)
        def wrapper_fixture(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper_fixture
    return decorator_fixture
