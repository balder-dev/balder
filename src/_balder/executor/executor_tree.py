from __future__ import annotations
from typing import Union, List, Type, TYPE_CHECKING

from _balder.executor.setup_executor import SetupExecutor
from _balder.executor.basic_executor import BasicExecutor
from _balder.fixture_manager import FixtureManager
from _balder.testresult import ResultState, BranchBodyResult
from _balder.previous_executor_mark import PreviousExecutorMark

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.executor.scenario_executor import ScenarioExecutor
    from _balder.executor.variation_executor import VariationExecutor
    from _balder.executor.testcase_executor import TestcaseExecutor


class ExecutorTree(BasicExecutor):
    """
    This class is the root object of the executor tree structure
    """

    def __init__(self, fixture_manager: FixtureManager):
        super().__init__()
        self._setup_executors: List[SetupExecutor] = []
        self._fixture_manager = fixture_manager

        # contains the result object for the BODY part of this branch (will be overwritten in :class:`TestcaseExecutor`)
        self.body_result = BranchBodyResult(self)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_child_executors(self) -> List[BasicExecutor]:
        return self._setup_executors

    @property
    def base_instance(self) -> object:
        """returns None because this element is a ExecutorTree"""
        return None

    @property
    def fixture_manager(self) -> FixtureManager:
        """returns the fixture manager of this tree"""
        return self._fixture_manager

    @property
    def parent_executor(self) -> None:
        return None

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _prepare_execution(self):
        pass

    def _body_execution(self):
        for cur_setup_executor in self.get_setup_executors():
            if cur_setup_executor.has_runnable_elements():
                cur_setup_executor.execute()
            elif cur_setup_executor.prev_mark == PreviousExecutorMark.SKIP:
                cur_setup_executor.set_result_for_whole_branch(ResultState.SKIP)
            elif cur_setup_executor.prev_mark == PreviousExecutorMark.COVERED_BY:
                cur_setup_executor.set_result_for_whole_branch(ResultState.COVERED_BY)
            else:
                cur_setup_executor.set_result_for_whole_branch(ResultState.NOT_RUN)

    def _cleanup_execution(self):
        pass

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_setup_executors(self) -> List[SetupExecutor]:
        """returns all setup executors of this tree"""
        return self._setup_executors

    def get_all_scenario_executors(self) -> List[ScenarioExecutor]:
        """
        returns a list with all scenario executors
        """
        all_scenario_executor = []
        for cur_setup_executor in self.get_setup_executors():
            all_scenario_executor += cur_setup_executor.get_scenario_executors()
        return all_scenario_executor

    def get_all_variation_executors(self) -> List[VariationExecutor]:
        """
        returns a list with all variation executors
        """
        all_variation_executor = []
        for cur_scenario_executor in self.get_all_scenario_executors():
            all_variation_executor += cur_scenario_executor.variation_executors
        return all_variation_executor

    def get_all_testcase_executors(self) -> List[TestcaseExecutor]:
        """
        returns a list with all testcase executors
        """
        all_testcase_executor = []
        for cur_scenario_executor in self.get_all_scenario_executors():
            for cur_variation_executor in cur_scenario_executor.variation_executors:
                all_testcase_executor += cur_variation_executor.testcase_executors
        return all_testcase_executor

    def add_setup_executor(self, setup_executor: SetupExecutor):
        """
        This method adds a new :class:`SetupExecutor` to the child element's list of this tree object
        """
        if not isinstance(setup_executor, SetupExecutor):
            raise TypeError("the given object `setup_executor` must be of type `SetupExecutor`")
        if setup_executor in self._setup_executors:
            raise ValueError("the given object `setup_executor` already exists in child list")
        self._setup_executors.append(setup_executor)

    def get_executor_for_setup(self, setup: Type[Setup]) -> Union[SetupExecutor, None]:
        """
        This method searches for a SetupExecutor in the internal list for the given :class:`Setup` type

        :param setup: the setup class for which the executor is being searched for

        :return: returns the associated SetupExecutor or None if there are no matches for the given type
        """
        for cur_setup_executor in self._setup_executors:
            if cur_setup_executor.base_setup_class.__class__ == setup:
                return cur_setup_executor
        # can not find some
        return None

    def cleanup_empty_executor_branches(self):
        to_remove_executor = []
        for cur_setup_executor in self.get_setup_executors():
            cur_setup_executor.cleanup_empty_executor_branches()
            if len(cur_setup_executor.get_scenario_executors()) == 0:
                # remove this whole executor because it has no children anymore
                to_remove_executor.append(cur_setup_executor)
        for cur_setup_executor in to_remove_executor:
            self._setup_executors.remove(cur_setup_executor)

    def execute(self) -> None:
        """
        This method executes this branch of the tree
        """
        start_text = "START TESTSESSION"
        end_text = "FINISH TESTSESSION"
        line_length = 120

        def print_line(text):
            full_text = int((line_length - (len(start_text) + 2)) / 2) * "=" + " " + text + " "
            full_text += "=" * (line_length - len(full_text))
            print(full_text)

        print_line(start_text)
        # check if there exists runnable elements
        runnables = [cur_exec.has_runnable_elements() for cur_exec in self.get_setup_executors()]
        one_or_more_runnable_setups = None if len(runnables) == 0 else max(runnables)
        if one_or_more_runnable_setups:
            super().execute()
        else:
            print("NO EXECUTABLE SETUPS/SCENARIOS FOUND")
        print_line(end_text)
        summary = self.testsummary()
        is_first = True
        for cur_key, cur_val in summary.items():
            if is_first:
                is_first = False
            else:
                print(" | ", end="")
            print(f"TOTAL {cur_key.value}: {cur_val}", end="")
        print("")

    def print_tree(self) -> None:
        """this method is an auxiliary method which outputs the entire tree"""
        print("RESOLVING OVERVIEW", end="\n\n")
        for cur_setup_executor in self.get_setup_executors():
            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                for cur_variation_executor in cur_scenario_executor.variation_executors:
                    print(f"Scenario `{cur_scenario_executor.base_scenario_class.__class__.__qualname__}` <-> "
                          f"Setup `{cur_setup_executor.base_setup_class.__class__.__qualname__}`")
                    mapping_printings = {}
                    for cur_scenario_device, cur_setup_device in cur_variation_executor.base_device_mapping.items():
                        mapping_printings[f"   {cur_scenario_device.__qualname__}"] = str(cur_setup_device.__qualname__)
                    max_len = max(len(cur_elem) for cur_elem in mapping_printings.keys())
                    for cur_key, cur_val in mapping_printings.items():
                        print(("{:<" + str(max_len) + "} = {}").format(cur_key, cur_val))
                    for cur_testcase_excutor in cur_variation_executor.testcase_executors:
                        print(f"   -> Testcase<{cur_testcase_excutor.base_testcase_callable.__qualname__}>")
