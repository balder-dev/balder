from __future__ import annotations

import time
from typing import TYPE_CHECKING

import sys

import traceback
from abc import ABC, abstractmethod

from _balder.executor.basic_executor import BasicExecutor
from _balder.testresult import ResultState

if TYPE_CHECKING:
    from _balder.fixture_execution_level import FixtureExecutionLevel
    from _balder.fixture_manager import FixtureManager


class BasicExecutableExecutor(BasicExecutor, ABC):
    """
    The BasicExecutor class is an abstract class that represents the parent class of all executors. Together with other
    executor classes, an executor forms a tree structure in which individual tests, which later on are executed, are
    assigned to individual scenarios
    """
    fixture_execution_level: FixtureExecutionLevel = None

    def __init__(self):
        super().__init__()

        # holds the execution time of this branch (with branch fixtures)
        self.execution_time_sec = None

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    @abstractmethod
    def fixture_manager(self) -> FixtureManager:
        """returns the active fixture manager instance"""

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

    def set_result_for_whole_branch(self, value: ResultState):
        """
        This method sets the executor result for all sub executors.

        :param value: the new value that should be set for this branch
        """
        if value not in (ResultState.SKIP, ResultState.COVERED_BY, ResultState.NOT_RUN):
            raise ValueError("can not set a state that is not NOT_RUN, SKIP or COVERED_BY for a whole branch")
        if self.all_child_executors is None:
            self.body_result.set_result(result=value, exception=None)
        else:
            for cur_child_executor in self.all_child_executors:
                cur_child_executor.set_result_for_whole_branch(value)

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
        if self.all_child_executors:
            for cur_child_executor in self.all_child_executors:
                cur_child_executor.filter_tree_for_user_filters()

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
                else:
                    self.construct_result.set_result(ResultState.NOT_RUN)

                self._body_execution(show_discarded=show_discarded)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # this has to be a construction fixture error
                traceback.print_exception(*sys.exc_info())
                self.construct_result.set_result(ResultState.ERROR, exc)
            finally:
                if self.has_runnable_tests():
                    if self.fixture_manager.is_allowed_to_leave(self):
                        self.fixture_manager.leave(self)
                        self.teardown_result.set_result(ResultState.SUCCESS)
                else:
                    self.teardown_result.set_result(ResultState.NOT_RUN)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # this has to be a teardown fixture error
            traceback.print_exception(*sys.exc_info())
            self.teardown_result.set_result(ResultState.ERROR, exc)

        self._cleanup_execution(show_discarded=show_discarded)

        self.execution_time_sec = time.perf_counter() - start_time
