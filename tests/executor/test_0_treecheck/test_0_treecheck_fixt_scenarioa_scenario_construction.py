from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0TreecheckFixtScenarioaScenarioConstruction(Base0EnvtesterClass):
    """
    This testcase executes the basic envtester and forces an error on a specific given position. The test checks if the
    system behaviour is as expected.

    file: ``scenarios/scenario_a.py``
    class: ``ScenarioA``
    method/function: ``fixture_scenario``
    part: ``construction``
    """

    @property
    def cmd_args(self):
        return [
            '--test-error-file', 'scenarios/scenario_a.py',
            '--test-error-cls', 'ScenarioA',
            '--test-error-meth', 'fixture_scenario',
            '--test-error-part', 'construction',
        ]

    @property
    def expected_exit_code(self):
        return 1

    @property
    def expected_data(self):
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            [
                (
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_session
                    {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_session
                    {"cls": "SetupB", "meth": "fixture_session", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
                    {"cls": "ScenarioA", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: ScenarioB.fixture_session
                    {"cls": "ScenarioB", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
                    {"cls": "SetupA", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioA.fixture_setup
                    {"cls": "ScenarioA", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
                    {"cls": "SetupA", "meth": "fixture_scenario", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioA.fixture_scenario
                    {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "construction"},

                    # stop here - also skip teardown code where error occurred
                    # {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "teardown"},

                    # FIXTURE-TEARDOWN: SetupA.fixture_scenario
                    {"cls": "SetupA", "meth": "fixture_scenario", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                    # FIXTURE-TEARDOWN: ScenarioA.fixture_setup
                    {"cls": "ScenarioA", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_setup
                    {"cls": "SetupA", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_setup
                    {"cls": "SetupB", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioB.fixture_setup
                    {"cls": "ScenarioB", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_scenario
                    {"cls": "SetupB", "meth": "fixture_scenario", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioB.fixture_scenario
                    {"cls": "ScenarioB", "meth": "fixture_scenario", "part": "construction"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                    {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_variation
                    {"cls": "SetupB", "meth": "fixture_variation", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioB.fixture_variation
                    {"cls": "ScenarioB", "meth": "fixture_variation", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    [
                        (
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_testcase
                            {"cls": "SetupB", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioB.fixture_testcase
                            {"cls": "ScenarioB", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # TESTCASE: ScenarioA.test_b_1
                            {"cls": "ScenarioB", "meth": "test_b_1"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: ScenarioB.fixture_testcase
                            {"cls": "ScenarioB", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_testcase
                            {"cls": "SetupB", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                        ),
                        (
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_testcase
                            {"cls": "SetupB", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioB.fixture_testcase
                            {"cls": "ScenarioB", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # TESTCASE: ScenarioA.test_b_2
                            {"cls": "ScenarioB", "meth": "test_b_2"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: ScenarioB.fixture_testcase
                            {"cls": "ScenarioB", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_testcase
                            {"cls": "SetupB", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                        ),
                    ],
                    # FIXTURE-TEARDOWN: ScenarioB.fixture_variation
                    {"cls": "ScenarioB", "meth": "fixture_variation", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupB.fixture_variation
                    {"cls": "SetupB", "meth": "fixture_variation", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_variation
                    {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                    # FIXTURE-TEARDOWN: ScenarioB.fixture_scenario
                    {"cls": "ScenarioB", "meth": "fixture_scenario", "part": "teardown"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupB.fixture_scenario
                    {"cls": "SetupB", "meth": "fixture_scenario", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                    # FIXTURE-TEARDOWN: ScenarioB.fixture_setup
                    {"cls": "ScenarioB", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupB.fixture_setup
                    {"cls": "SetupB", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
                ),
            ],
            [
                (
                    # FIXTURE-TEARDOWN: ScenarioA.fixture_session
                    {"cls": "ScenarioA", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: ScenarioB.fixture_session
                    {"cls": "ScenarioB", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-TEARDOWN: SetupA.fixture_session
                    {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: SetupA.fixture_session
                    {"cls": "SetupB", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.ERROR, "test session does not terminates with ERROR"

        assert session.executor_tree.construct_result.result == ResultState.SUCCESS, \
            "global executor tree construct part does not set ResultState.SUCCESS"
        assert session.executor_tree.body_result.result == ResultState.ERROR, \
            "global executor tree body part does not set ResultState.ERROR"
        assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
            "global executor tree teardown part does not set ResultState.NOT_RUN"
        for cur_setup_executor in session.executor_tree.get_setup_executors():
            if cur_setup_executor.base_setup_class.__class__.__name__ == "SetupA":
                assert cur_setup_executor.executor_result == ResultState.ERROR, \
                    "the setup executor does not have result ERROR"

                assert cur_setup_executor.construct_result.result == ResultState.SUCCESS
                assert cur_setup_executor.body_result.result == ResultState.ERROR
                assert cur_setup_executor.teardown_result.result == ResultState.SUCCESS
            else:
                # this is the setup for the scenario that works successfully
                assert cur_setup_executor.executor_result == ResultState.SUCCESS, \
                    "the setup executor does not have result SUCCESS"

                assert cur_setup_executor.construct_result.result == ResultState.SUCCESS
                assert cur_setup_executor.body_result.result == ResultState.SUCCESS
                assert cur_setup_executor.teardown_result.result == ResultState.SUCCESS

            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                if cur_scenario_executor.base_scenario_class.__class__.__name__ == "ScenarioA":
                    assert cur_scenario_executor.executor_result == ResultState.ERROR, \
                        "the scenario executor does not have result ERROR"

                    assert cur_scenario_executor.construct_result.result == ResultState.ERROR
                    assert cur_scenario_executor.body_result.result == ResultState.NOT_RUN
                    # success here because other items were already run in this section
                    assert cur_scenario_executor.teardown_result.result == ResultState.SUCCESS

                    for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                        assert cur_variation_executor.executor_result == ResultState.NOT_RUN, \
                            "the variation executor does not have result NOT_RUN"

                        assert cur_variation_executor.construct_result.result == ResultState.NOT_RUN
                        assert cur_variation_executor.body_result.result == ResultState.NOT_RUN
                        assert cur_variation_executor.teardown_result.result == ResultState.NOT_RUN

                        for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                            assert cur_testcase_executor.executor_result == ResultState.NOT_RUN, \
                                "the testcase executor does not have result NOT_RUN"

                            assert cur_testcase_executor.construct_result.result == ResultState.NOT_RUN
                            assert cur_testcase_executor.body_result.result == ResultState.NOT_RUN
                            assert cur_testcase_executor.teardown_result.result == ResultState.NOT_RUN
                else:
                    # everything was successfully
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
