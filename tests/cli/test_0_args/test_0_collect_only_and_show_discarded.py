from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from ...test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0CollectOnlyAndShowDiscarded(Base0EnvtesterClass):
    """
    This testcase executes the basic ENV example with a specific command line argument
    ``--collect-only --show-discarded``.

    The test checks that no tests are executed and the printed information is like expected. It makes sure, that the
    ``--show-discarded`` argument is ignored.
    """

    @property
    def cmd_args(self):
        return ['--collect-only', '--show-discarded']

    @property
    def expected_data(self) -> tuple:
        return tuple()

    def validate_printed_output(self, stdout: str) -> bool:
        assert self._check_header_of_stdout(stdout, 2, 2), \
            f"problems within header output"
        assert len(stdout.splitlines()) == 5, f"detect more output lines (={len(stdout.splitlines())}) than expected"
        return True

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # make sure that  no executor tree was created
        assert session.executor_tree is None, f"executor tree is not None"
