from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from ...test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0NoMatchBecausePatternSwitched(Base0EnvtesterClass):
    """
    This testcase executes the basic example and checks if the tree ends with the result SUCCESS. It calls the balder
    environment with the following filter patterns for setup and for scenarios and validates that the correct tests are
    executed:

    `balder .. --only-with-scenario setups/setup*.py --only-with-setup scenarios/scenario_*.py`

    No elements should be executed here.
    """
    @property
    def cmd_args(self):
        return ["--only-with-scenario", "setups/setup*.py", "--only-with-setup", "scenarios/scenario_*.py"]

    @property
    def expected_data(self):
        return ()

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.NOT_RUN, \
            "test session does not terminates with NOT RUN"
