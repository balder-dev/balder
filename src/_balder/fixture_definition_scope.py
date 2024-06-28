from __future__ import annotations
from typing import List
from enum import Enum


class FixtureDefinitionScope(Enum):
    """
    This enum describes the definition scope of a fixture. A definition scope is the position the fixture was defined.
    If the fixture was defined within the balderglob.py file, it has the definition-scope `GLOB`. If it is defined
    within a scenario or setup it has the equivalent SCENARIO or SETUP scope.
    """
    GLOB = 'glob'
    SETUP = 'setup'
    SCENARIO = 'scenario'

    @classmethod
    def get_order(cls) -> List[FixtureDefinitionScope]:
        """returns the priority order of the fixture definition scope"""
        return [cls.GLOB, cls.SETUP, cls.SCENARIO]
