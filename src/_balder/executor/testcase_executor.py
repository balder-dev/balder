from __future__ import annotations
from typing import Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.executor.variation_executor import VariationExecutor
    from _balder.scenario import Scenario

import sys
import time
import traceback
from _balder.utils import inspect_method
from _balder.testresult import ResultState, TestcaseResult
from _balder.executor.basic_executor import BasicExecutor
from _balder.previous_executor_mark import PreviousExecutorMark


class TestcaseExecutor(BasicExecutor):
    """
    A TestcaseExecutor class represents an actual single test that can be executed. It therefore references exactly to a
    test method of a scenario that can be executed on the specific setup this executor belongs to.
    """

    def __init__(self, testcase: callable, parent: VariationExecutor):
        super(TestcaseExecutor, self).__init__()
        from _balder.fixture_manager import FixtureManager

        self._base_testcase_callable = testcase
        self._parent_executor = parent
        self._fixture_manager: FixtureManager = parent.fixture_manager

        # if there exist executors that cover this item, they are contained as list in this property
        self.covered_by_executors = None

        self.execution_time_sec = None

        # contains the result object for the BODY part of this branch
        self.body_result = TestcaseResult(self)

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
    def base_instance(self) -> object:
        """
        returns the base class instance to which this executor instance belongs"""
        return self._base_testcase_callable

    @property
    def base_testcase_callable(self) -> callable:
        return self._base_testcase_callable

    @property
    def base_testcase_obj(self) -> Scenario:
        """
        return the testcase Scenario this testcase is defined in
        """
        return self._parent_executor.cur_scenario_class

    @property
    def fixture_manager(self):
        return self._fixture_manager

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def has_runnable_elements(self) -> bool:
        return self.prev_mark == PreviousExecutorMark.RUNNABLE

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

    def cleanup_empty_executor_branches(self):
        """
        This method searches the whole tree and removes branches where an executor item has no own children. It can
        remove these branches, because they have no valid matchings.

        This method implementation of the :class:`TestcaseExecutor` does nothing.
        """
        pass

    def get_covered_by_element(self) -> List[Union[Scenario, callable]]:
        """
        This method returns a list of elements where the whole scenario is covered from. This means, that the whole
        test methods in this scenario are already be covered from every single element in the list.
        """
        all_covered_by_data = []
        scenario_executor = self.parent_executor.parent_executor
        scenario_class = scenario_executor.base_scenario_class
        covered_by_dict_resolved = scenario_executor.get_covered_by_dict()
        if self.base_testcase_callable in covered_by_dict_resolved.keys():
            all_covered_by_data += covered_by_dict_resolved[self.base_testcase_callable]
        if scenario_class in covered_by_dict_resolved.keys():
            all_covered_by_data += covered_by_dict_resolved[scenario_class]
        return all_covered_by_data

    def execute(self) -> None:
        """
        This method executes this testcase.
        """
        print(f"      TEST {self.base_testcase_callable.__qualname__} ", end='')
        if self.should_be_skipped():
            self.body_result.set_result(ResultState.SKIP)
            self.execution_time_sec = 0
            print("[S]")
            return
        try:
            try:
                self.fixture_manager.enter(self)

                start_time = time.perf_counter()
                try:
                    _, func_type = inspect_method(self.base_testcase_callable)
                    all_args = self.fixture_manager.get_all_attribute_values(
                        self, self.base_testcase_obj.__class__, self.base_testcase_callable, func_type)
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
                except:
                    traceback.print_exception(*sys.exc_info())
                    self.body_result.set_result(ResultState.FAILURE)
                finally:
                    self.execution_time_sec = time.perf_counter() - start_time
            except:
                # we can catch everything, because error is already documented
                traceback.print_exception(*sys.exc_info())
            if self.fixture_manager.is_allowed_to_leave(self):
                self.fixture_manager.leave(self)
            print(f"[{self.body_result.get_result_as_char()}]")
        except:
            # we can catch everything, because error is already documented
            traceback.print_exception(*sys.exc_info())
