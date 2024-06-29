from __future__ import annotations

import pathlib
import sys
import traceback
from typing import Callable, Optional, Union, List
from _balder.exit_code import ExitCode
from _balder.testresult import ResultState
from _balder.exceptions import BalderException
from _balder.balder_session import BalderSession


def console_balder(cmd_args: Optional[List[str]] = None, working_dir: Union[str, pathlib.Path, None] = None):
    """script that executes a balder session"""
    _console_balder_debug(cmd_args=cmd_args, working_dir=working_dir)


# pylint: disable-next=too-many-arguments
def _console_balder_debug(cmd_args: Optional[List[str]] = None, working_dir: Union[str, pathlib.Path, None] = None,
                          cb_session_created: Optional[Callable] = None, cb_run_finished: Optional[Callable] = None,
                          cb_balder_exc: Optional[Callable] = None, cb_unexpected_exc: Optional[Callable] = None):
    """helper balder execution that allows more debug access"""
    try:
        balder_session = BalderSession(cmd_args=cmd_args, working_dir=working_dir)

        if cb_session_created:
            cb_session_created(balder_session)

        balder_session.run()

        if cb_run_finished:
            cb_run_finished(balder_session)

        if balder_session.executor_tree is None:
            sys.exit(ExitCode.SUCCESS.value)
        elif balder_session.executor_tree.executor_result == ResultState.SUCCESS:
            sys.exit(ExitCode.SUCCESS.value)
        elif balder_session.executor_tree.executor_result in [ResultState.ERROR, ResultState.FAILURE]:
            # check if a BalderException was thrown too -> would be a balder environment error -> special exit code
            balder_exceptions = [cur_exc for cur_exc in balder_session.executor_tree.get_all_recognized_exception()
                                 if isinstance(cur_exc, BalderException)]
            if len(balder_exceptions) > 0:
                sys.exit(ExitCode.BALDER_USAGE_ERROR.value)
            else:
                sys.exit(ExitCode.TESTS_FAILED.value)

    except BalderException as exc:
        # a balder usage error occurs
        if cb_balder_exc:
            cb_balder_exc(exc)
        traceback.print_exception(*sys.exc_info())
        sys.exit(ExitCode.BALDER_USAGE_ERROR.value)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # a unexpected error occurs
        if cb_unexpected_exc:
            cb_unexpected_exc(exc)
        traceback.print_exception(*sys.exc_info())
        sys.exit(ExitCode.UNEXPECTED_ERROR.value)
