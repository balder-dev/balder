from __future__ import annotations
from typing import Type, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.scenario import Scenario
    from _balder.fixture_manager import FixtureManager
    from _balder.executor.executor_tree import ExecutorTree

import sys
import traceback
from _balder.testresult import ResultState, BranchBodyResult
from _balder.executor.basic_executor import BasicExecutor
from _balder.executor.scenario_executor import ScenarioExecutor
from _balder.previous_executor_mark import PreviousExecutorMark


class SetupExecutor(BasicExecutor):
    """
    A SetupExecutor is the highest branch object of an :class:`ExecutorTree`. It contains all scenarios and the
    underlying device mappings and their test cases that exist with this setup.
    """

    def __init__(self, setup: Type[Setup], parent: ExecutorTree):
        super(SetupExecutor, self).__init__()
        self._scenario_executors: List[ScenarioExecutor] = []
        # check if instance already exists
        if hasattr(setup, "_instance") and setup._instance is not None and isinstance(setup._instance, setup):
            self._base_setup_class = setup._instance
        else:
            self._base_setup_class = setup()
            setup._instance = self._base_setup_class
        self._parent_executor = parent
        self._fixture_manager = parent.fixture_manager

        # contains the result object for the BODY part of this branch
        self.body_result = BranchBodyResult(self)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_child_executors(self) -> List[ScenarioExecutor]:
        return self.scenario_executors

    @property
    def parent_executor(self) -> ExecutorTree:
        return self._parent_executor

    @property
    def base_instance(self) -> object:
        """returns the base class instance to which this executor instance belongs"""
        return self.base_setup_class

    @property
    def base_setup_class(self) -> Setup:
        return self._base_setup_class

    @property
    def scenario_executors(self) -> List[ScenarioExecutor]:
        return self._scenario_executors

    @property
    def fixture_manager(self) -> FixtureManager:
        return self._fixture_manager

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def cleanup_empty_executor_branches(self):
        to_remove_executor = []
        for cur_scenario_executor in self.scenario_executors:
            cur_scenario_executor.cleanup_empty_executor_branches()
            if len(cur_scenario_executor.variation_executors) == 0:
                # remove this whole executor because it has no children anymore
                to_remove_executor.append(cur_scenario_executor)
        for cur_scenario_executor in to_remove_executor:
            self._scenario_executors.remove(cur_scenario_executor)

    def add_scenario_executor(self, scenario_executor: ScenarioExecutor):
        """
        This method adds a new ScenarioExecutor to the child element list of the tree
        """
        if not isinstance(scenario_executor, ScenarioExecutor):
            raise TypeError("the given object `scenario_executor` must be of type type `ScenarioExecutor`")
        if scenario_executor in self._scenario_executors:
            raise ValueError("the given object `scenario_executor` already exists in child list")
        self._scenario_executors.append(scenario_executor)

    def get_executor_for_scenario(self, scenario: Type[Scenario]) -> Union[ScenarioExecutor, None]:
        """
        This method searches for a ScenarioExecutor in the internal list for which the given scenario is
        contained in

        :param scenario: the scenario class for which the executor should be searched for

        :return: returns the associated ScenarioExecutor or None if no matching could be found
        """
        for cur_scenario_executor in self._scenario_executors:
            if cur_scenario_executor.base_scenario_class.__class__ == scenario:
                return cur_scenario_executor
        # can not find some
        return None

    def execute(self) -> None:
        """
        This method executes this branch of the tree
        """
        print(f"SETUP {self.base_setup_class.__class__.__name__}")
        try:
            try:
                self.fixture_manager.enter(self)

                for cur_scenario_executor in self.scenario_executors:
                    if cur_scenario_executor.has_runnable_elements():
                        cur_scenario_executor.execute()
                    elif cur_scenario_executor.prev_mark == PreviousExecutorMark.SKIP:
                        cur_scenario_executor.set_result_for_whole_branch(ResultState.SKIP)
                    elif cur_scenario_executor.prev_mark == PreviousExecutorMark.COVERED_BY:
                        cur_scenario_executor.set_result_for_whole_branch(ResultState.COVERED_BY)
                    else:
                        cur_scenario_executor.set_result_for_whole_branch(ResultState.NOT_RUN)
            except:
                # we can catch everything, because error is already documented
                traceback.print_exception(*sys.exc_info())
            if self.fixture_manager.is_allowed_to_leave(self):
                self.fixture_manager.leave(self)
        except:
            # we can catch everything, because error is already documented
            traceback.print_exception(*sys.exc_info())
