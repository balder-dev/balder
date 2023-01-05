from __future__ import annotations

import pathlib
import sys
import traceback
from typing import Callable, Optional, Union, List
from _balder.exceptions import BalderException
from _balder.balder_session import BalderSession


def console_balder(cmd_args: Optional[List[str]] = None, working_dir: Union[str, pathlib.Path, None] = None):
    """script that executes a balder session"""
    _console_balder_debug(cmd_args=cmd_args, working_dir=working_dir)


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

    except BalderException as exc:
        # a balder usage error occurs
        if cb_balder_exc:
            cb_balder_exc(exc)
        traceback.print_exception(*sys.exc_info())
    except Exception as exc:
        # a unexpected error occurs
        if cb_unexpected_exc:
            cb_unexpected_exc(exc)
        traceback.print_exception(*sys.exc_info())
