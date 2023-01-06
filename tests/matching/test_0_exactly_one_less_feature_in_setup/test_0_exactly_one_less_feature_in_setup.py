from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ExactlyOneLessFeatureInSetup(Base0EnvtesterClass):
    """
    This testcase uses a reduced version of the basic envtester environment. It should have no matching between the
    ``ScenarioA`` and the ``SetupA`` because the ``SetupDevice1`` does not provide an implementation of ``FeatureIII``.
    """

    @property
    def expected_data(self) -> tuple:
        return ()

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.NOT_RUN, \
            "test session does not terminates with NOT_RUN"

        assert session.executor_tree.construct_result.result == ResultState.NOT_RUN, \
            "global executor tree construct part does not set ResultState.NOT_RUN"
        assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
            "global executor tree body part does not set ResultState.SUCCESS"
        assert session.executor_tree.teardown_result.result == ResultState.NOT_RUN, \
            "global executor tree teardown part does not set ResultState.NOT_RUN"
