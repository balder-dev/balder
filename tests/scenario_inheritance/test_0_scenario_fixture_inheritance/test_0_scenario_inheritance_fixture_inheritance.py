import pathlib
import sys

from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_scenario_inheritance_fixture_inheritance(balder_working_dir):
    """
    This testcase executes the basic ENVTESTER environment. Additionally, it provides a child scenario class per
    scenario. One of it (the `ScenarioAChild`) defines no own fixtures, while the other (the `ScenarioBChild`)
    overwrites some fixtures. The test expects, that only the overwritten fixtures are executed. No scenario should
    inherit fixtures from a higher class without redefining and decorating it.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):

    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    session.run()
    print("\n")

    # get the class instance from already imported module - balder loads it from given working directory
    RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
    runtime_data = RuntimeObserver.data.copy()

    exec_list = []
    for cur_data in runtime_data:
        new_data = cur_data.copy()
        new_data["file"] = pathlib.Path(new_data["file"]).relative_to(env_dir)
        exec_list.append(new_data)

    expected_data = (
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
        # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_session
        {"cls": "ScenarioBChild", "meth": "fixture_session", "part": "construction"},
        {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
        [
            (
                # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
                {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
                # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
                {"cls": "SetupA", "meth": "fixture_setup", "part": "construction"},
                {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
                {"cls": "SetupA", "meth": "fixture_scenario", "part": "construction"},
                {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                # FIXTURE-CONSTRUCTION: SetupA.fixture_variation
                {"cls": "SetupA", "meth": "fixture_variation", "part": "construction"},
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
                        # TESTCASE: ScenarioAChild.test_a_1
                        {"cls": "ScenarioAChild", "meth": "test_a_1"},
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
                        # TESTCASE: ScenarioAChild.test_a_2
                        {"cls": "ScenarioAChild", "meth": "test_a_2"},
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
                # FIXTURE-TEARDOWN: SetupA.fixture_variation
                {"cls": "SetupA", "meth": "fixture_variation", "part": "teardown"},
                {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: balderglob_fixture_variation
                {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                # FIXTURE-TEARDOWN: SetupA.fixture_scenario
                {"cls": "SetupA", "meth": "fixture_scenario", "part": "teardown"},
                {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
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
                # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_setup
                {"cls": "ScenarioBChild", "meth": "fixture_setup", "part": "construction"},
                {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                # FIXTURE-CONSTRUCTION: SetupB.fixture_scenario
                {"cls": "SetupB", "meth": "fixture_scenario", "part": "construction"},
                {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_scenario
                {"cls": "ScenarioBChild", "meth": "fixture_scenario", "part": "construction"},
                {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                # FIXTURE-CONSTRUCTION: SetupB.fixture_variation
                {"cls": "SetupB", "meth": "fixture_variation", "part": "construction"},
                {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_variation
                {"cls": "ScenarioBChild", "meth": "fixture_variation", "part": "construction"},
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
                        # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_testcase
                        {"cls": "ScenarioBChild", "meth": "fixture_testcase", "part": "construction"},
                        {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                        {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                        # TESTCASE: ScenarioBChild.test_b_1
                        {"cls": "ScenarioBChild", "meth": "test_b_1"},
                        {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                        {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                        # FIXTURE-TEARDOWN: ScenarioBChild.fixture_testcase
                        {"cls": "ScenarioBChild", "meth": "fixture_testcase", "part": "teardown"},
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
                        # FIXTURE-CONSTRUCTION: ScenarioBChild.fixture_testcase
                        {"cls": "ScenarioBChild", "meth": "fixture_testcase", "part": "construction"},
                        {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                        {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                        # TESTCASE: ScenarioA.test_b_2
                        {"cls": "ScenarioBChild", "meth": "test_b_2"},
                        {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                        {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                        # FIXTURE-TEARDOWN: ScenarioBChild.fixture_testcase
                        {"cls": "ScenarioBChild", "meth": "fixture_testcase", "part": "teardown"},
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
                # FIXTURE-TEARDOWN: ScenarioBChild.fixture_variation
                {"cls": "ScenarioBChild", "meth": "fixture_variation", "part": "teardown"},
                {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: SetupB.fixture_variation
                {"cls": "SetupB", "meth": "fixture_variation", "part": "teardown"},
                {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: balderglob_fixture_variation
                {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                # FIXTURE-TEARDOWN: ScenarioBChild.fixture_scenario
                {"cls": "ScenarioBChild", "meth": "fixture_scenario", "part": "teardown"},
                {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: SetupB.fixture_scenario
                {"cls": "SetupB", "meth": "fixture_scenario", "part": "teardown"},
                {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                # FIXTURE-TEARDOWN: ScenarioBChild.fixture_setup
                {"cls": "ScenarioBChild", "meth": "fixture_setup", "part": "teardown"},
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
        # FIXTURE-TEARDOWN: ScenarioBChild.fixture_session
        {"cls": "ScenarioBChild", "meth": "fixture_session", "part": "teardown"},
        {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
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

    compare_observed_list_with_expected(exec_list, expected_data)

    # check result states everywhere (have to be SUCCESS everywhere
    assert session.executor_tree.executor_result == ResultState.SUCCESS, "test session does not terminates with success"

    assert session.executor_tree.construct_result.result == ResultState.SUCCESS, \
        "global executor tree construct part does not set ResultState.SUCCESS"
    assert session.executor_tree.body_result.result == ResultState.SUCCESS, \
        "global executor tree body part does not set ResultState.SUCCESS"
    assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
        "global executor tree teardown part does not set ResultState.SUCCESS"
    for cur_setup_executor in session.executor_tree.setup_executors:
        assert cur_setup_executor.executor_result == ResultState.SUCCESS, \
            "the setup executor does not have result SUCCESS"

        assert cur_setup_executor.construct_result.result == ResultState.SUCCESS
        assert cur_setup_executor.body_result.result == ResultState.SUCCESS
        assert cur_setup_executor.teardown_result.result == ResultState.SUCCESS

        for cur_scenario_executor in cur_setup_executor.scenario_executors:
            assert cur_scenario_executor.executor_result == ResultState.SUCCESS, \
                "the scenario executor does not have result SUCCESS"

            assert cur_scenario_executor.construct_result.result == ResultState.SUCCESS
            assert cur_scenario_executor.body_result.result == ResultState.SUCCESS
            assert cur_scenario_executor.teardown_result.result == ResultState.SUCCESS

            for cur_variation_executor in cur_scenario_executor.variation_executors:
                assert cur_variation_executor.executor_result == ResultState.SUCCESS, \
                    "the variation executor does not have result SUCCESS"

                assert cur_variation_executor.construct_result.result == ResultState.SUCCESS
                assert cur_variation_executor.body_result.result == ResultState.SUCCESS
                assert cur_variation_executor.teardown_result.result == ResultState.SUCCESS

                for cur_testcase_executor in cur_variation_executor.testcase_executors:
                    assert cur_testcase_executor.executor_result == ResultState.SUCCESS, \
                        "the testcase executor does not have result SUCCESS"

                    assert cur_testcase_executor.construct_result.result == ResultState.SUCCESS
                    assert cur_testcase_executor.body_result.result == ResultState.SUCCESS
                    assert cur_testcase_executor.teardown_result.result == ResultState.SUCCESS
