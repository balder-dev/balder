import pathlib
import sys

from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_instancemethod_fixture(balder_working_dir):
    """
    This testcase executes the envtester environment. This is a reduced version of the environment tester. The test
    checks if fixtures that are defined as normal methods (only in scenario and setup class) work as expected.

    For this the following will be checked:

    * fixture will be called correctly
    * parameters are given correctly (self will be set correctly)
    * return value of fixture will be forwarded correctly

    The environment implements fixture in the definition scopes BALDERGLOB, SETUP and SCENARIO with all possible
    execution levels. It has one setup and one scenario class that use instance method fixtures only. The test uses
    the following fixtures to secure that parameter and return values are managed correctly:

    **Class SetupA**:

    * ``fixture_setup_session`` expects parameters ``balderglob_fixture_session``
    * ``fixture_setup_setup`` expects parameters ``balderglob_fixture_setup`` and ``fixture_setup_session``
    * ``fixture_setup_scenario`` expects parameters ``balderglob_fixture_scenario`` and ``fixture_setup_setup``
    * ``fixture_setup_variation`` expects parameters ``balderglob_fixture_variation`` and ``fixture_scenario``
    * ``fixture_setup_testcase`` expects parameters ``balderglob_fixture_testcase`` and ``fixture_setup_variation``

    **Class ScenarioA**:

    * ``fixture_scenario_session`` expects parameters ``balderglob_fixture_session`` and ``fixture_setup_session``
    * ``fixture_scenario_setup`` expects parameters ``balderglob_fixture_setup``, ``fixture_setup_setup`` and
      ``fixture_scenario_session``
    * ``fixture_scenario_scenario`` expects parameters ``balderglob_fixture_scenario``, ``fixture_setup_scenario`` and
      ``fixture_scenario_setup``
    * ``fixture_scenario_variation`` expects parameters ``balderglob_fixture_variation``, ``fixture_setup_variation``
      and ``fixture_scenario_scenario``
    * ``fixture_scenario_testcase`` expects parameters ``balderglob_fixture_testcase``, ``fixture_setup_testcase`` and
      ``fixture_scenario_variation``

    The testcase method validates the return values for all scenario and setup fixtures.
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
        # FIXTURE-CONSTRUCTION: SetupA.fixture_session
        {"cls": "SetupA", "meth": "fixture_setup_session", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
        {"cls": "ScenarioA", "meth": "fixture_scenario_session", "part": "construction"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
        {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
        # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
        {"cls": "SetupA", "meth": "fixture_setup_setup", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_setup
        {"cls": "ScenarioA", "meth": "fixture_scenario_setup", "part": "construction"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
        {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
        # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
        {"cls": "SetupA", "meth": "fixture_setup_scenario", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_scenario
        {"cls": "ScenarioA", "meth": "fixture_scenario_scenario", "part": "construction"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
        {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
        # FIXTURE-CONSTRUCTION: SetupA.fixture_variation
        {"cls": "SetupA", "meth": "fixture_setup_variation", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_variation
        {"cls": "ScenarioA", "meth": "fixture_scenario_variation", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
        {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
        # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
        {"cls": "SetupA", "meth": "fixture_setup_testcase", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_testcase
        {"cls": "ScenarioA", "meth": "fixture_scenario_testcase", "part": "construction"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # TESTCASE: ScenarioA.test_a_1
        {"cls": "ScenarioA", "meth": "test_a_1"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: ScenarioA.fixture_testcase
        {"cls": "ScenarioA", "meth": "fixture_scenario_testcase", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: SetupA.fixture_testcase
        {"cls": "SetupA", "meth": "fixture_setup_testcase", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: balderglob_fixture_testcase
        {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
        # FIXTURE-TEARDOWN: ScenarioA.fixture_variation
        {"cls": "ScenarioA", "meth": "fixture_scenario_variation", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: SetupA.fixture_variation
        {"cls": "SetupA", "meth": "fixture_setup_variation", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: balderglob_fixture_variation
        {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
        # FIXTURE-TEARDOWN: ScenarioA.fixture_scenario
        {"cls": "ScenarioA", "meth": "fixture_scenario_scenario", "part": "teardown"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: SetupA.fixture_scenario
        {"cls": "SetupA", "meth": "fixture_setup_scenario", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: balderglob_fixture_scenario
        {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
        # FIXTURE-TEARDOWN: ScenarioA.fixture_setup
        {"cls": "ScenarioA", "meth": "fixture_scenario_setup", "part": "teardown"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: SetupA.fixture_setup
        {"cls": "SetupA", "meth": "fixture_setup_setup", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: balderglob_fixture_setup
        {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
        # FIXTURE-TEARDOWN: ScenarioA.fixture_session
        {"cls": "ScenarioA", "meth": "fixture_scenario_session", "part": "teardown"},
        {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
        # FIXTURE-TEARDOWN: SetupA.fixture_session
        {"cls": "SetupA", "meth": "fixture_setup_session", "part": "teardown"},
        {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
        {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
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
