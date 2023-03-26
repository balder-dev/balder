from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0UnclearSetupScopedFixtureReference(Base0EnvtesterClass):
    """
    This testcase executes the basic envtester example. It forces the setup to throw a validation error for the
    unclear-setup-scoped-fixture-reference problematic.

    The problem:
        A scenario scoped fixture (defined in a scenario) with the execution level SESSION references a fixture (over
        an argument) with a name that is also used for one or more setup scoped fixtures with execution level SESSION.

        For this constellation it is unclear which referenced setup scoped fixture is the correct one.

    For this the ScenarioA references a fixture `unclear_fixture`. The SetupA implements this fixture. This should
    produce this error. Both fixtures are on SESSION level.
    """

    @property
    def expected_exit_code(self) -> int:
        return 4

    @property
    def expected_data(self) -> tuple:
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "unclear_fixture", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # error occurs here
            # FIXTURE-TEARDOWN: SetupA.fixture_session
            {"cls": "SetupA", "meth": "unclear_fixture", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.ERROR, \
            "test session does not terminates with an ERROR state"

        assert session.executor_tree.construct_result.result == ResultState.ERROR, \
            "global executor tree construct part does not set ResultState.SUCCESS"
        assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
            "global executor tree body part does not set ResultState.NOT_RUN"
        assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
            "global executor tree teardown part does not set ResultState.SUCCESS"
        for cur_setup_executor in session.executor_tree.get_setup_executors():
            assert cur_setup_executor.executor_result == ResultState.NOT_RUN, \
                "the setup executor does not have result NOT_RUN"

            assert cur_setup_executor.construct_result.result == ResultState.NOT_RUN
            assert cur_setup_executor.body_result.result == ResultState.NOT_RUN
            assert cur_setup_executor.teardown_result.result == ResultState.NOT_RUN

            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                assert cur_scenario_executor.executor_result == ResultState.NOT_RUN, \
                    "the scenario executor does not have result NOT_RUN"

                assert cur_scenario_executor.construct_result.result == ResultState.NOT_RUN
                assert cur_scenario_executor.body_result.result == ResultState.NOT_RUN
                assert cur_scenario_executor.teardown_result.result == ResultState.NOT_RUN

                for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                    assert cur_variation_executor.executor_result == ResultState.NOT_RUN, \
                        "the variation executor does not have result SUCCESS"

                    assert cur_variation_executor.construct_result.result == ResultState.NOT_RUN
                    assert cur_variation_executor.body_result.result == ResultState.NOT_RUN
                    assert cur_variation_executor.teardown_result.result == ResultState.NOT_RUN

                    for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                        assert cur_testcase_executor.executor_result == ResultState.NOT_RUN, \
                            "the testcase executor does not have result SUCCESS"

                        assert cur_testcase_executor.construct_result.result == ResultState.NOT_RUN
                        assert cur_testcase_executor.body_result.result == ResultState.NOT_RUN
                        assert cur_testcase_executor.teardown_result.result == ResultState.NOT_RUN
