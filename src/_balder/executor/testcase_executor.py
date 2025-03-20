from __future__ import annotations
from typing import List, Union, TYPE_CHECKING

import sys
import time
import traceback

from _balder.executor.basic_executable_executor import BasicExecutableExecutor
from _balder.fixture_execution_level import FixtureExecutionLevel
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.testresult import ResultState, TestcaseResult
from _balder.utils.functions import get_method_type
from _balder.utils.mixin_can_be_covered_by_executor import MixinCanBeCoveredByExecutor

if TYPE_CHECKING:
    from _balder.executor.scenario_executor import ScenarioExecutor
    from _balder.executor.variation_executor import VariationExecutor
    from _balder.fixture_manager import FixtureManager
    from _balder.scenario import Scenario


class TestcaseExecutor(BasicExecutableExecutor, MixinCanBeCoveredByExecutor):
    """
    A TestcaseExecutor class represents an actual single test that can be executed. It therefore references exactly to a
    test method of a scenario that can be executed on the specific setup this executor belongs to.
    """
    fixture_execution_level = FixtureExecutionLevel.TESTCASE

    def __init__(
            self,
            testcase: callable,
            parent: VariationExecutor,
    ) -> None:
        super().__init__()

        self._base_testcase_callable = testcase
        self._parent_executor = parent
        self._fixture_manager: FixtureManager = parent.fixture_manager

        # if there exist executors that cover this item, they are contained as list in this property
        self.covered_by_executors = None

        # contains the result object for the BODY part of this branch
        self.body_result = TestcaseResult(self)

        # holds the raw test execution time in seconds
        self.test_execution_time_sec = 0

        # determine prev_mark IGNORE/SKIP for the testcase
        if self.should_be_skipped():
            self.prev_mark = PreviousExecutorMark.SKIP
        # always overwrite if it should be ignored
        if self.should_be_ignored():
            self.prev_mark = PreviousExecutorMark.IGNORE

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_child_executors(self) -> None:
        return None

    @property
    def parent_executor(self) -> VariationExecutor:
        return self._parent_executor

    @property
    def scenario_executor(self) -> ScenarioExecutor:
        return self.parent_executor.parent_executor

    @property
    def base_instance(self) -> object:
        """
        returns the base class instance to which this executor instance belongs"""
        return self._base_testcase_callable

    @property
    def base_testcase_callable(self) -> callable:
        """returns the testcase function"""
        return self._base_testcase_callable

    @property
    def base_testcase_obj(self) -> Scenario:
        """
        return the testcase Scenario this testcase is defined in
        """
        return self._parent_executor.cur_scenario_class

    @property
    def fixture_manager(self):
        """returns the current active fixture manager"""
        return self._fixture_manager

    @property
    def full_test_name_str(self) -> str:
        """
        returns the name of the test method, that should be used in output
        """
        return self._base_testcase_callable.__qualname__

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _prepare_execution(self, show_discarded):
        print(f"      TEST {self.full_test_name_str} ", end='')

    def _body_execution(self, show_discarded):
        self.test_execution_time_sec = 0

        if self.should_be_skipped():
            self.body_result.set_result(ResultState.SKIP)
            return
        if self.should_be_ignored():
            self.body_result.set_result(ResultState.NOT_RUN)
            return
        if self.is_covered_by():
            self.body_result.set_result(ResultState.COVERED_BY)
            return

        start_time = time.perf_counter()
        try:
            func_type = get_method_type(self.base_testcase_obj.__class__, self.base_testcase_callable)
            all_args = self.get_all_test_method_args()
            if func_type == "staticmethod":
                # testcase is a staticmethod - no special first attribute
                self.base_testcase_callable(**all_args)
            elif func_type == "classmethod":
                self.base_testcase_callable(self=self.base_testcase_obj.__class__, **all_args)
            elif func_type == "instancemethod":
                self.base_testcase_callable(self=self.base_testcase_obj, **all_args)
            else:
                # `function` is not allowed here!
                raise ValueError(f"found illegal value for func_type `{func_type}` for test "
                                 f"`{self.base_testcase_callable.__name__}`")

            self.body_result.set_result(ResultState.SUCCESS)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # this has to be a test error
            traceback.print_exception(*sys.exc_info())
            self.body_result.set_result(ResultState.FAILURE, exc)
        self.test_execution_time_sec = time.perf_counter() - start_time

    def _cleanup_execution(self, show_discarded):
        print(f"[{self.body_result.get_result_as_char()}]")

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def should_run(self):
        """returns true if the testcase should be executed (defined in scenario)"""
        if self.base_testcase_callable in self.parent_executor.parent_executor.all_run_tests:
            return True
        return False

    def should_be_skipped(self):
        """returns true if the testcase should be skipped (defined in scenario)"""
        if self.base_testcase_callable in self.parent_executor.parent_executor.all_skip_tests:
            return True
        return False

    def should_be_ignored(self):
        """returns true if the testcase should be ignored (defined in scenario)"""
        if self.base_testcase_callable in self.parent_executor.parent_executor.all_ignore_tests:
            return True
        return False

    def is_covered_by(self):
        """returns true if the testcase is covered-by"""
        return self.prev_mark == PreviousExecutorMark.COVERED_BY

    def has_skipped_tests(self) -> bool:
        return self.prev_mark == PreviousExecutorMark.SKIP

    def has_covered_by_tests(self) -> bool:
        return self.prev_mark == PreviousExecutorMark.COVERED_BY

    def cleanup_empty_executor_branches(self, consider_discarded=False):
        """
        This method searches the whole tree and removes branches where an executor item has no own children. It can
        remove these branches, because they have no valid matchings.

        This method implementation of the :class:`TestcaseExecutor` does nothing.
        """

    def get_covered_by_element(self) -> List[Union[Scenario, callable]]:
        covered_by_dict = self.scenario_executor.base_scenario_controller.get_abs_covered_by_dict()
        all_covered_by_data = covered_by_dict.get(self.base_testcase_callable.__name__, [])
        # also add all scenario specified covered-by elements
        all_covered_by_data.extend(covered_by_dict.get(None, []))
        return all_covered_by_data

    def get_all_test_method_args(self):
        """
        returns all kwargs values for the test method
        """
        func_type = get_method_type(self.base_testcase_obj.__class__, self.base_testcase_callable)
        return self.fixture_manager.get_all_attribute_values(
            self,
            self.base_testcase_obj.__class__,
            self.base_testcase_callable,
            func_type
        )
