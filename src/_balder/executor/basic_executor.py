from __future__ import annotations

import time
from typing import List, Dict, Union, Type, TYPE_CHECKING

import sys
import types
import traceback
from abc import ABC, abstractmethod
from _balder.testresult import FixturePartResult, ResultState
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.testresult import TestcaseResult

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.scenario import Scenario
    from _balder.fixture_manager import FixtureManager


class BasicExecutor(ABC):
    """
    The BasicExecutor class is an abstract class that represents the parent class of all executors. Together with other
    executor classes, an executor forms a tree structure in which individual tests, which later on are executed, are
    assigned to individual scenarios
    """
    # this property describes the runnable state of the executor branch before the executor is really used
    #  with this you can declare a whole branch as inactive, while the collecting process is active
    prev_mark = PreviousExecutorMark.RUNNABLE

    def __init__(self):
        # contains the result object for the CONSTRUCT FIXTURE part of this branch
        self.construct_result = FixturePartResult(self)
        # contains the result object for the BODY part of this branch (will be defined in subclasses)
        self.body_result = None
        # contains the result object for the TEARDOWN FIXTURE part of this branch
        self.teardown_result = FixturePartResult(self)

        # holds the execution time of this branch (with branch fixtures)
        self.execution_time_sec = None

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    @abstractmethod
    def all_child_executors(self) -> List[BasicExecutor]:
        """
        returns all child executors of this object or None if no child executors can exist (this element is a leaf)
        """

    @property
    @abstractmethod
    def parent_executor(self) -> BasicExecutor:
        """returns the parent executor of this element"""

    @property
    @abstractmethod
    def base_instance(self) -> object:
        """returns the base class instance to which this executor instance belongs or None if this element is a
        ExecutorTree"""

    @property
    @abstractmethod
    def fixture_manager(self) -> FixtureManager:
        """returns the active fixture manager instance"""

    @property
    def executor_result(self) -> ResultState:
        """
        This property returns the combined state of this executor object. This is determined by its properties
        ``construct_result``, ``body_result`` and ``teardown_result``.
        """
        relative_result = ResultState.NOT_RUN
        priority_order = ResultState.priority_order()

        if priority_order.index(self.construct_result.result) < priority_order.index(relative_result):
            relative_result = self.construct_result.result
        if priority_order.index(self.body_result.result) < priority_order.index(relative_result):
            relative_result = self.body_result.result
        if priority_order.index(self.teardown_result.result) < priority_order.index(relative_result):
            relative_result = self.teardown_result.result
        return relative_result

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    @abstractmethod
    def _prepare_execution(self, show_discarded):
        """
        This method runs before the branch will be executed and before the fixture construction code of this branch
        runs.
        """

    @abstractmethod
    def _body_execution(self, show_discarded):
        """
        This method runs between the fixture construction and teardown code. It should trigger the execution of the
        child branches.
        """

    @abstractmethod
    def _cleanup_execution(self, show_discarded):
        """
        This method runs after the branch was executed (also after the fixture teardown code ran)
        """

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_all_recognized_exception(self) -> List[Exception]:
        """
        This method returns all occurred Exception of this branch.

        :return: a list with all occurred and recorded exceptions
        """
        all_own = [self.construct_result.exception, self.body_result.exception, self.teardown_result.exception]
        if self.all_child_executors:
            for cur_child_executor in self.all_child_executors:
                all_own += cur_child_executor.get_all_recognized_exception()

        # filter all duplicated entries
        all_own = list(set(all_own))
        if None in all_own:
            all_own.remove(None)
        return all_own

    def set_result_for_whole_branch(self, value: ResultState):
        """
        This method sets the executor result for all sub executors.

        :param value: the new value that should be set for this branch
        """
        if value not in (ResultState.SKIP, ResultState.COVERED_BY, ResultState.NOT_RUN):
            raise ValueError("can not set a state that is not NOT_RUN, SKIP or COVERED_BY for a whole branch")
        for cur_child_executor in self.all_child_executors:
            if isinstance(cur_child_executor.body_result, TestcaseResult):
                cur_child_executor.body_result.set_result(result=value, exception=None)

    def has_runnable_tests(self, consider_discarded_too=False) -> bool:
        """
        This method returns true if this executor element is runnable. The method returns true if this element has
        `prev_mark=RUNNABLE` and minimum one of its children has `prev_mark=RUNNABLE` too.

        :param consider_discarded_too: True if the method allows DISCARDED elements too
        """
        allowed_prev_marks = [PreviousExecutorMark.RUNNABLE]

        if consider_discarded_too:
            allowed_prev_marks.append(PreviousExecutorMark.DISCARDED)

        if self.prev_mark not in allowed_prev_marks:
            return False

        if self.all_child_executors is not None:
            # the executor has child executors -> check them
            for cur_child in self.all_child_executors:
                if cur_child.has_runnable_tests(consider_discarded_too):
                    return True
            return False
        return True

    def get_all_base_instances_of_this_branch(
            self, with_type: Union[Type[Setup], Type[Scenario], Type[types.FunctionType]],
            only_runnable_elements: bool = True) -> List[Union[Setup, Scenario, object]]:
        """
        This method returns a list of all base instance elements that are from given type `with_type`. If `with_type`
        is a base type of this branch element, the method always returns a list with one element. If the base instance
        element is a child of the current branch, it could be a list with zero to infinite elements.

        .. note::
            The method only returns unique objects.
        """
        # search all higher classes and this one (if there is a match, return value is a list with exactly one element)
        cur_executor = self
        # only go through cur_executor == ExecutorTree (do not iterate with this object)
        while cur_executor.parent_executor is not None:
            if isinstance(cur_executor.base_instance, with_type):
                if not only_runnable_elements or cur_executor.has_runnable_tests():
                    return [cur_executor.base_instance]
            cur_executor = cur_executor.parent_executor

        # go in the branch and search in all children (recursively)
        result = []
        # if there are no child executors -> we do not need to search in children because there are no children
        if self.all_child_executors is not None:
            for cur_child_executor in self.all_child_executors:
                child_result = cur_child_executor.get_all_base_instances_of_this_branch(
                    with_type=with_type, only_runnable_elements=only_runnable_elements)
                result += child_result
        # remove duplicate items
        return list(set(result))

    @abstractmethod
    def cleanup_empty_executor_branches(self, consider_discarded=False):
        """
        This method searches the whole tree and removes branches where an executor item has no own children. It can
        remove these branches, because they have no valid matchings.

        :param consider_discarded: true if this method should consider discarded branches, otherwise False
        """

    def filter_tree_for_user_filters(self):
        """
        This method calls all user defined filters that are to be applied to the executor tree.
        """
        for cur_child_executor in self.all_child_executors:
            cur_child_executor.filter_tree_for_user_filters()

    def testsummary(self) -> Dict[ResultState, int]:
        """
        returns a dictionary with all possible :class:`ResultState` as keys and the number of times they have occurred
        in this branch as values
        """

        summary = {
            ResultState.NOT_RUN: 0,
            ResultState.FAILURE: 0,
            ResultState.ERROR: 0,
            ResultState.SUCCESS: 0,
            ResultState.SKIP: 0,
            ResultState.COVERED_BY: 0
        }

        if isinstance(self.body_result, TestcaseResult):
            summary[self.executor_result] = 1
        else:
            for cur_child_exec in self.all_child_executors:
                cur_child_dict = cur_child_exec.testsummary()
                for cur_key in cur_child_dict.keys():
                    if cur_key in summary:
                        summary[cur_key] += cur_child_dict[cur_key]
                    else:
                        summary[cur_key] = cur_child_dict[cur_key]
        return summary

    def execute(self, show_discarded=False):
        """
        Executes the whole branch
        """
        start_time = time.perf_counter()
        self._prepare_execution(show_discarded=show_discarded)

        try:
            try:
                if self.has_runnable_tests():
                    self.fixture_manager.enter(self)
                    self.construct_result.set_result(ResultState.SUCCESS)

                self._body_execution(show_discarded=show_discarded)
            except Exception as exc:
                # this has to be a construction fixture error
                traceback.print_exception(*sys.exc_info())
                self.construct_result.set_result(ResultState.ERROR, exc)
            finally:
                if self.has_runnable_tests():
                    if self.fixture_manager.is_allowed_to_leave(self):
                        self.fixture_manager.leave(self)
                        self.teardown_result.set_result(ResultState.SUCCESS)
        except Exception as exc:
            # this has to be a teardown fixture error
            traceback.print_exception(*sys.exc_info())
            self.teardown_result.set_result(ResultState.ERROR, exc)

        self._cleanup_execution(show_discarded=show_discarded)

        self.execution_time_sec = time.perf_counter() - start_time
