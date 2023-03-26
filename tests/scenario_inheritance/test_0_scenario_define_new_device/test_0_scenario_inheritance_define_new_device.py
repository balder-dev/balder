from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ScenarioInheritanceDefineNewDevice(Base0EnvtesterClass):
    """
    This testcase executes the basic envtester environment, but with a `ScenarioAParent` and its child class
    `ScenarioAChild`. The parent class does not define the device `ScenarioDevice2`. This class will be defined only in
    the `ScenarioAChild`.

    The test secures that the environment works as expected.
    """

    @property
    def expected_data(self) -> tuple:
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_session
            {"cls": "ScenarioAChild", "meth": "fixture_session", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
            {"cls": "SetupA", "meth": "fixture_setup", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_setup
            {"cls": "ScenarioAChild", "meth": "fixture_setup", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
            {"cls": "SetupA", "meth": "fixture_scenario", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_scenario
            {"cls": "ScenarioAChild", "meth": "fixture_scenario", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_variation
            {"cls": "SetupA", "meth": "fixture_variation", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_variation
            {"cls": "ScenarioAChild", "meth": "fixture_variation", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            [
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_testcase
                    {"cls": "ScenarioAChild", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # TESTCASE: ScenarioAChild.test_a_1
                    {"cls": "ScenarioAChild", "meth": "test_a_1"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: ScenarioAChild.fixture_testcase
                    {"cls": "ScenarioAChild", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioAChild.fixture_testcase
                    {"cls": "ScenarioAChild", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # TESTCASE: ScenarioAChild.test_a_2
                    {"cls": "ScenarioAChild", "meth": "test_a_2"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: ScenarioAChild.fixture_testcase
                    {"cls": "ScenarioAChild", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                ),
            ],
            # FIXTURE-TEARDOWN: ScenarioAChild.fixture_variation
            {"cls": "ScenarioAChild", "meth": "fixture_variation", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: SetupA.fixture_variation
            {"cls": "SetupA", "meth": "fixture_variation", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
            # FIXTURE-TEARDOWN: ScenarioAChild.fixture_scenario
            {"cls": "ScenarioAChild", "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: SetupA.fixture_scenario
            {"cls": "SetupA", "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
            # FIXTURE-TEARDOWN: ScenarioAChild.fixture_setup
            {"cls": "ScenarioAChild", "meth": "fixture_setup", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: SetupA.fixture_setup
            {"cls": "SetupA", "meth": "fixture_setup", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
            # FIXTURE-TEARDOWN: ScenarioAChild.fixture_session
            {"cls": "ScenarioAChild", "meth": "fixture_session", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):

        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.SUCCESS, \
            "test session does not terminates with success"

        assert session.executor_tree.construct_result.result == ResultState.SUCCESS, \
            "global executor tree construct part does not set ResultState.SUCCESS"
        assert session.executor_tree.body_result.result == ResultState.SUCCESS, \
            "global executor tree body part does not set ResultState.SUCCESS"
        assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
            "global executor tree teardown part does not set ResultState.SUCCESS"
        for cur_setup_executor in session.executor_tree.get_setup_executors():
            assert cur_setup_executor.executor_result == ResultState.SUCCESS, \
                "the setup executor does not have result SUCCESS"

            assert cur_setup_executor.construct_result.result == ResultState.SUCCESS
            assert cur_setup_executor.body_result.result == ResultState.SUCCESS
            assert cur_setup_executor.teardown_result.result == ResultState.SUCCESS

            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                assert cur_scenario_executor.executor_result == ResultState.SUCCESS, \
                    "the scenario executor does not have result SUCCESS"

                assert cur_scenario_executor.construct_result.result == ResultState.SUCCESS
                assert cur_scenario_executor.body_result.result == ResultState.SUCCESS
                assert cur_scenario_executor.teardown_result.result == ResultState.SUCCESS

                for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                    assert cur_variation_executor.executor_result == ResultState.SUCCESS, \
                        "the variation executor does not have result SUCCESS"

                    assert cur_variation_executor.construct_result.result == ResultState.SUCCESS
                    assert cur_variation_executor.body_result.result == ResultState.SUCCESS
                    assert cur_variation_executor.teardown_result.result == ResultState.SUCCESS

                    for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                        assert cur_testcase_executor.executor_result == ResultState.SUCCESS, \
                            "the testcase executor does not have result SUCCESS"

                        assert cur_testcase_executor.construct_result.result == ResultState.SUCCESS
                        assert cur_testcase_executor.body_result.result == ResultState.SUCCESS
                        assert cur_testcase_executor.teardown_result.result == ResultState.SUCCESS
