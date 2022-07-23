from __future__ import annotations

from typing import Literal

import functools
from _balder.executor.executor_tree import ExecutorTree
from _balder.fixture_manager import FixtureManager


def fixture(level: Literal['session', 'setup', 'scenario', 'variation', 'testcase']):
    """
    This decorator declares the decorated function/method as a fixture function/method.

    :param level: the execution level the fixture should have
    """
    ALLOWED_LEVELS = FixtureManager.EXECUTION_LEVEL_ORDER

    if level not in ALLOWED_LEVELS:
        raise ValueError(f"the value of `level` must be a `str` with one of the values `{'`, `'.join(ALLOWED_LEVELS)}`")

    def decorator_fixture(func):
        # always add the fixture to FixtureManager.raw_fixtures - class determination will be done later by
        # :meth:`Collector`
        if not hasattr(ExecutorTree, 'raw_fixtures'):
            ExecutorTree.raw_fixtures = {}
        if level not in ExecutorTree.raw_fixtures.keys():
            ExecutorTree.raw_fixtures[level] = []
        ExecutorTree.raw_fixtures[level].append(func)

        @functools.wraps(func)
        def wrapper_fixture(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper_fixture
    return decorator_fixture

