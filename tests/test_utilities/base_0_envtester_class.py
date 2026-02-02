import re
import tempfile
from typing import List, Optional
import sys
import traceback
from typing import Union
from abc import ABC, abstractmethod
import pathlib
from contextlib import redirect_stdout
from multiprocessing import Process, Queue
from _balder.balder_session import BalderSession
from _balder.console.balder import _console_balder_debug
from _balder.exceptions import BalderException
from .observer_compare import compare_observed_list_with_expected


class Base0EnvtesterClass(ABC):
    """
    This is a base class for all tests that want to use the 0_envtester environment.
    """

    @property
    @abstractmethod
    def expected_data(self) -> tuple:
        """This property should return the expected data that should be sent by the process over the queue."""

    @property
    def expected_data_alternative(self) -> Union[tuple, None]:
        """
        optional property that can hold an alternative expected data (often required, if it is not clear at which
        branch will be executed first while an error is expected in one of them
        """
        return None

    @property
    def expected_exit_code(self) -> int:
        """returns the expected exit code the process should terminate"""
        return 0

    def validate_printed_output(self, stdout: str) -> bool:
        """
        Optional callback to validate expected printed output information on stdout.
        It should raise exceptions in case it detects any problems.

        :return: True if the data is valid, False otherwise (while it is preferred to use exceptions)
        """
        return True

    @classmethod
    def _check_header_of_stdout(
            cls,
            stdout: str,
            expected_scenarios: int,
            expected_setups: int,
            expected_variations: Optional[int] = None,
            expected_discarded: Optional[int] = None
    ) -> bool:
        re_expression = r"""^\+[-]+\+
\| BALDER Testsystem\s+\|
\|  python version .+? \| balder version .+?\s*\|
\+[-]+\+
"""
        re_expression += f"Collect {expected_setups} Setups and {expected_scenarios} Scenarios"

        if expected_variations:
            re_expression += f"\n  resolve them to {expected_variations} valid variations"
            if expected_discarded:
                re_expression += f" \({expected_discarded} discarded\)"
        return re.compile(re_expression, re.DOTALL | re.MULTILINE).match(stdout) is not None

    @property
    def cmd_args(self):
        """returns the command line arguments that should be used in the process call"""
        return []

    def test(self, balder_working_dir):
        """
        This is the general test method, that executes the balder process.
        """
        exec_log_queue = Queue(maxsize=0)

        with tempfile.TemporaryDirectory() as tempdir:
            temp_filepath = pathlib.Path(tempdir) / "stdout.txt"

            proc = Process(target=self.__class__.processed_method,
                           args=(balder_working_dir, self.cmd_args, exec_log_queue, temp_filepath,
                                 self.__class__.validate_finished_session, self.__class__.handle_balder_exception))
            proc.start()
            exec_list = []
            while proc.is_alive() or not exec_log_queue.empty():

                if not exec_log_queue.empty():
                    new_data = exec_log_queue.get()
                    new_data["file"] = pathlib.Path(new_data["file"]).relative_to(balder_working_dir)
                    exec_list.append(new_data)

            proc.join()

            with open(temp_filepath, 'r', encoding="utf-8") as stdout_file:
                process_stdout = stdout_file.read()
            print(process_stdout)

        assert proc.exitcode == self.expected_exit_code, \
            f"the process terminates with unexpected exit code `{proc.exitcode}` - exit code " \
            f"`{self.expected_exit_code}` was expected"

        if self.expected_data_alternative is None:
            # only one possible truth
            compare_observed_list_with_expected(exec_list, self.expected_data)
        else:
            # two possibilities are allowed
            error1 = None
            try:
                compare_observed_list_with_expected(exec_list, self.expected_data)
            except Exception as exc:
                error1 = exc
            error2 = None
            try:
                compare_observed_list_with_expected(exec_list, self.expected_data_alternative)
            except Exception as exc:
                error2 = exc
            if error1 and error2:
                # can not find possible matching
                raise error1

        assert self.validate_printed_output(process_stdout.strip()), f"detect issues with printed output"

    @staticmethod
    def processed_method(
            env_dir,
            args: List[str],
            queue: Queue,
            stdout_filepath: pathlib.Path,
            cb_validate_finished_session, cb_balder_exception):
        """
        This is the processed method

        :param env_dir: the directory path to the `env` directory for the current test

        :param args: a list with all command line arguments that should be used for the balder call

        :param queue: the queue the :class:RuntimeObserver` uses to communicate with the pytest process

        :param stdout_filepath: the file path to the file the stdout should be written to

        :param cb_validate_finished_session: a callback that validates the :class:`BalderSession`, after the session
                                             has finished

        :param cb_balder_exception: will be executed in case a balder error was thrown during collecting or resolving
        """
        # use the BalderSession object to import the balderglob file - than load the
        def set_queue(session):
            RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
            RuntimeObserver.queue = queue

        def cb_finished(session: BalderSession):
            try:
                cb_validate_finished_session(session)
            except Exception:
                traceback.print_exception(*sys.exc_info())
                exit(255)

        def cb_balder_exc(exception: BalderException):
            try:
                cb_balder_exception(exception)
            except Exception:
                traceback.print_exception(*sys.exc_info())
                exit(255)

        with open(stdout_filepath, "w", encoding="utf-8") as stdout_file:
            with redirect_stdout(stdout_file):
                _console_balder_debug(cmd_args=args, working_dir=env_dir, cb_session_created=set_queue,
                                      cb_run_finished=cb_finished, cb_balder_exc=cb_balder_exc)


    @staticmethod
    @abstractmethod
    def validate_finished_session(session: BalderSession):
        """
        This method can be used to validate the session after the process execution was finished. This method will be
        executed in separate test process!

        NOTE: All exception that are thrown inside this callback will result in status code 255

        :param session: the balder session object
        """

    @staticmethod
    def handle_balder_exception(exc: BalderException):
        """
        This callback can be used to handle an unexpected error

        :param exc: the exception that was thrown
        """
        pass
