from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, List, Union

from enum import Enum

if TYPE_CHECKING:
    from _balder.executor.basic_executor import BasicExecutor


class ResultState(Enum):
    """
    enumeration that describes the possible results of a testcase-/fixture-executor
    """
    # this state will be assigned if the executor doesn't run yet
    NOT_RUN = 'not_run'
    # this state will be assigned if the test fails (only assignable to :class:`TestcaseExecutor`)
    FAILURE = 'failure'
    # this state will be assigned if the executor can not be executed because the fixture fails (only possible in
    # construction part of fixtures, if the error occurs in teardown the next higher executer get this state) - will be
    # assigned to the executor which has the fixture that fails
    ERROR = 'error'
    # this state will be assigned if the executor was executed successfully (session fixture and teardown fixture; for
    # :class:`TestcaseExecutor` also the testcase itself)
    SUCCESS = 'success'
    # this state will be assigned if the executor was skipped
    SKIP = 'skip'
    # this state will be assigned if the executor is covered by another executor and wasn't executed (only assignable
    # to :class:`ScenarioExecutor` and :class:`TestcaseExecutor`)
    COVERED_BY = 'covered_by'

    @staticmethod
    def priority_order() -> List[ResultState]:
        """
        returns an order of states that returns the highest priority as first item and the lowest as last one
        """
        return [ResultState.ERROR, ResultState.FAILURE, ResultState.SUCCESS, ResultState.COVERED_BY, ResultState.SKIP,
                ResultState.NOT_RUN]


class _Result:

    def __init__(self, executor: BasicExecutor):
        self._result = ResultState.NOT_RUN

        self._related_executor = executor
        #: contains the exception that was thrown and returned into this result
        self.exception = None

        self.char_mapping = {
            ResultState.NOT_RUN: " ",
            ResultState.FAILURE: "X",
            ResultState.ERROR: "E",
            ResultState.SUCCESS: ".",
            ResultState.SKIP: "S",
            ResultState.COVERED_BY: "C"
        }

    def __str__(self):
        return self.result.name

    @property
    def result(self) -> ResultState:
        """returns the result"""
        return self._result

    def get_result_as_char(self):
        """
        returns a single char that represents the result state
        """

        return self.char_mapping[self.result]


class _SettableResult(_Result):
    ALLOWED_STATES = [ResultState.NOT_RUN, ResultState.FAILURE, ResultState.ERROR, ResultState.SUCCESS,
                      ResultState.SKIP, ResultState.COVERED_BY]

    def set_result(self, result: ResultState, exception: Union[Exception, None] = None) -> None:
        """this method allows to set the result - if the value is SKIP or COVERED_BY this method automatically sets this
        values also for all components of the branch in related executor"""

        if result not in self.ALLOWED_STATES:
            raise ValueError(
                f"it is not allowed to set the given result `{result.name}` in a ´{self.__class__.__name__}´")
        self._result = result
        self.exception = exception


class BranchBodyResult(_Result):
    """
    This result is used in every branch body. So it isn't set directly, it is always determined depending on the
    :class:`FixturePartResult` and :class:`TestcaseResult` of the executors children.
    """

    def __init__(self, executor: BasicExecutor):
        from _balder.executor.testcase_executor import TestcaseExecutor  # pylint: disable=import-outside-toplevel

        if isinstance(executor, TestcaseExecutor):
            raise TypeError("testcase executors are not allowed to use in `BranchBodyResult`")
        super().__init__(executor=executor)

    @property
    def result(self):
        """returns the determined result for the inner branch of the related executor"""
        relative_result = ResultState.NOT_RUN
        priority_order = ResultState.priority_order()
        if self._related_executor.all_child_executors:
            for cur_child in self._related_executor.all_child_executors:
                if priority_order.index(cur_child.executor_result) < priority_order.index(relative_result):
                    relative_result = cur_child.executor_result
        self._result = relative_result
        return self._result


class FixturePartResult(_SettableResult):
    """
    This result is used for fixture construct or teardown code. It describes if there was an error in the construct
    or teardown part of the fixture code for an executor.
    """
    #: contains the possible values that can be set for this Result type
    ALLOWED_STATES = [ResultState.NOT_RUN, ResultState.ERROR, ResultState.SUCCESS]


class TestcaseResult(_SettableResult):
    """
    This result is used for real executed testcase methods. These elements can only be assigned to real testcase methods
    which are only available in :class:`TestcaseExecutor`.
    """
    #: contains the possible values that can be set for this Result type
    ALLOWED_STATES = [ResultState.NOT_RUN, ResultState.FAILURE, ResultState.SUCCESS, ResultState.SKIP,
                      ResultState.COVERED_BY]

@dataclass
class ResultSummary:
    """
    object that holds the test results for multiple tests like on branch or global level
    """
    # this state will be assigned if the executor doesn't run yet
    not_run: int = 0
    # this state will be assigned if the test fails (only assignable to :class:`TestcaseExecutor`)
    failure: int = 0
    # this state will be assigned if the executor can not be executed because the fixture fails (only possible in
    # construction part of fixtures, if the error occurs in teardown the next higher executer get this state) - will be
    # assigned to the executor which has the fixture that fails
    error: int = 0
    # this state will be assigned if the executor was executed successfully (session fixture and teardown fixture; for
    # :class:`TestcaseExecutor` also the testcase itself)
    success: int = 0
    # this state will be assigned if the executor was skipped
    skip: int = 0
    # this state will be assigned if the executor is covered by another executor and wasn't executed (only assignable
    # to :class:`ScenarioExecutor` and :class:`TestcaseExecutor`)
    covered_by: int = 0

    def __add__(self, other) -> ResultSummary:
        new_summary = ResultSummary()
        for cur_field in fields(self.__class__):
            self_val = getattr(self, cur_field.name)
            other_val = getattr(other, cur_field.name)
            setattr(new_summary, cur_field.name, self_val + other_val)
        return new_summary
