from __future__ import annotations
from typing import List
from enum import Enum


class FixtureExecutionLevel(Enum):
    """
    This enum describes the fixture-execution-level of a fixture. It describes when the fixture should be executed. This
    level will be set in the fixture decorator.
    """
    SESSION = 'session'
    SETUP = 'setup'
    SCENARIO = 'scenario'
    VARIATION = 'variation'
    TESTCASE = 'testcase'

    @classmethod
    def get_order(cls) -> List[FixtureExecutionLevel]:
        """
        returns the execution order of fixtures
        """
        return [cls.SESSION, cls.SETUP, cls.SCENARIO, cls.VARIATION, cls.TESTCASE]
