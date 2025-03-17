from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from _balder.scenario import Scenario
    from _balder.executor.scenario_executor import ScenarioExecutor


class MixinCanBeCoveredByExecutor(ABC):
    """mixin class for executor that can hold covered-by items"""

    @property
    @abstractmethod
    def scenario_executor(self) -> ScenarioExecutor:
        """
        returns the current active scenario executor
        """

    @abstractmethod
    def get_covered_by_element(self) -> list[Scenario | callable]:
        """
        This method returns a list of elements where the elements of the executor are covered from.
        """
