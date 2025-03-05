from __future__ import annotations
from typing import Type, Union, List, TYPE_CHECKING

from _balder.fixture_execution_level import FixtureExecutionLevel
from _balder.testresult import ResultState, BranchBodyResult
from _balder.executor.basic_executable_executor import BasicExecutableExecutor
from _balder.executor.variation_executor import VariationExecutor
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.controllers.scenario_controller import ScenarioController

if TYPE_CHECKING:
    from _balder.scenario import Scenario
    from _balder.executor.setup_executor import SetupExecutor
    from _balder.fixture_manager import FixtureManager


class ScenarioExecutor(BasicExecutableExecutor):
    """
    A ScenarioExecutor can contain :meth:`VariationExecutor` as children.
    """
    fixture_execution_level = FixtureExecutionLevel.SCENARIO

    def __init__(self, scenario: Type[Scenario], parent: SetupExecutor):
        super().__init__()
        self._variation_executors: List[VariationExecutor] = []
        # check if instance already exists
        if hasattr(scenario, "_instance") and scenario._instance is not None and \
                isinstance(scenario._instance, scenario):
            self._base_scenario_class = scenario._instance
        else:
            self._base_scenario_class = scenario()
            scenario._instance = self._base_scenario_class
        self._parent_executor = parent
        self._fixture_manager = parent.fixture_manager

        # contains the result object for the BODY part of this branch
        self.body_result = BranchBodyResult(self)

        # if the related scenario class of this executor is decorated with ``@covered_by``, this property contains a
        # list with the :class:`ScenarioExecutor` or/and :class:`TestcaseExecutor` that covers this one
        self.covered_by_executors = None

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_child_executors(self) -> List[VariationExecutor]:
        return self._variation_executors

    @property
    def parent_executor(self) -> SetupExecutor:
        return self._parent_executor

    @property
    def base_instance(self) -> object:
        """
        returns the base class instance to which this executor instance belongs
        """
        return self.base_scenario_class

    @property
    def base_scenario_class(self) -> Scenario:
        """returns the :class:`Scenario` class that belongs to this executor"""
        return self._base_scenario_class

    @property
    def base_scenario_controller(self) -> ScenarioController:
        """returns the :class:`ScenarioController` for the setup object of this executor"""
        return ScenarioController.get_for(self.base_scenario_class.__class__)

    @property
    def fixture_manager(self) -> FixtureManager:
        """returns the current active fixture manager that belongs to this scenario executor"""
        return self._fixture_manager

    @property
    def all_run_tests(self) -> List[callable]:
        """returns a list of all test methods that are declared to `RUN` in their base :class:`Scenario` class"""
        return self.base_scenario_controller.get_run_test_methods()

    @property
    def all_skip_tests(self) -> List[callable]:
        """returns a list of all test methods that are declared to `SKIP` in their base :class:`Scenario` class"""
        return self.base_scenario_controller.get_skip_test_methods()

    @property
    def all_ignore_tests(self) -> List[callable]:
        """returns a list of all test methods that are declared to `IGNORE` in their base :class:`Scenario` class"""
        return self.base_scenario_controller.get_ignore_test_methods()

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _prepare_execution(self, show_discarded):
        print(f"  SCENARIO {self.base_scenario_class.__class__.__name__}")

    def _body_execution(self, show_discarded):
        for cur_variation_executor in self.get_variation_executors(return_discarded=show_discarded):
            prev_mark = cur_variation_executor.prev_mark
            if cur_variation_executor.has_runnable_tests() or cur_variation_executor.has_skipped_tests():
                cur_variation_executor.execute(show_discarded=show_discarded)
            elif prev_mark == PreviousExecutorMark.SKIP:
                cur_variation_executor.set_result_for_whole_branch(ResultState.SKIP)
            elif prev_mark == PreviousExecutorMark.COVERED_BY:
                cur_variation_executor.set_result_for_whole_branch(ResultState.COVERED_BY)
            else:
                cur_variation_executor.set_result_for_whole_branch(ResultState.NOT_RUN)

    def _cleanup_execution(self, show_discarded):
        pass

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_variation_executors(self, return_discarded=False) -> List[VariationExecutor]:
        """
        :param return_discarded: True if the method should return discarded variations too

        :return: returns all variation executors that are child executor of this scenario executor
        """
        if not return_discarded:
            return [cur_executor for cur_executor in self._variation_executors
                    if cur_executor.prev_mark != PreviousExecutorMark.DISCARDED]
        return self._variation_executors

    def cleanup_empty_executor_branches(self, consider_discarded=False):
        """
        This method removes all sub executors that are empty and not relevant anymore.
        """
        to_remove_executor = []
        for cur_variation_executor in self.get_variation_executors(return_discarded=consider_discarded):
            if len(cur_variation_executor.get_testcase_executors()) == 0:
                # remove this whole executor because it has no children anymore
                to_remove_executor.append(cur_variation_executor)
        for cur_variation_executor in to_remove_executor:
            self._variation_executors.remove(cur_variation_executor)

    def get_covered_by_element(self) -> List[Union[Scenario, callable]]:
        """
        This method returns a list of elements where the whole scenario is covered from. This means, that the whole
        test methods in this scenario are already be covered from one of the elements in the list.
        """
        return self.base_scenario_controller.get_abs_covered_by_dict().get(None, [])

    def add_variation_executor(self, variation_executor: VariationExecutor):
        """
        This method adds a new VariationExecutor to the child element list of the tree
        """
        if not isinstance(variation_executor, VariationExecutor):
            raise TypeError("the given object `variation_executor` must be of type `VariationExecutor`")
        if variation_executor in self._variation_executors:
            raise ValueError("the given object `variation_executor` already exists in child list")
        self._variation_executors.append(variation_executor)

    def get_executor_for_device_mapping(self, device_mapping: dict) -> Union[VariationExecutor, None]:
        """
        This method searches for a VariationExecutor in the internal list for which the given device mapping is
        contained in

        :param device_mapping: the device_mapping dictionary for which the executor should be searched for

        :return: returns the associated VariationExecutor or None if no matching could be found
        """
        for cur_variation_executor in self._variation_executors:
            if cur_variation_executor.base_device_mapping == device_mapping:
                return cur_variation_executor
        # can not find some
        return None
