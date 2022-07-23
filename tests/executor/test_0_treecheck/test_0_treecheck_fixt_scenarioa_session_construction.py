import pathlib
import sys
from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_treecheck_fixt_scenarioa_session_construction(balder_working_dir):
    """
    This testcase executes the basic envtester and forces an error on a specific given position. The test checks if the
    system behaviour is as expected.

    file: ``scenarios/scenario_a.py``
    class: ``ScenarioA``
    method/function: ``fixture_session``
    part: ``construction``
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):

    print("\n", flush=True)
    session = BalderSession(cmd_args=[
        '--test-error-file', str(env_dir.joinpath('scenarios/scenario_a.py')),
        '--test-error-cls', 'ScenarioA',
        '--test-error-meth', 'fixture_session',
        '--test-error-part', 'construction',
    ],
        working_dir=env_dir)
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

    expected_data_1 = (
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
        # FIXTURE-CONSTRUCTION: ScenarioB.fixture_session
        {"cls": "ScenarioB", "meth": "fixture_session", "part": "construction"},
        {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
        {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
        {"cls": "ScenarioA", "meth": "fixture_session", "part": "construction"},
        # stops execution here (only valid if the ScenarioB fixture was called first)
        # {"cls": "ScenarioA", "meth": "fixture_session", "part": "teardown"},

        # FIXTURE-TEARDOWN: ScenarioB.fixture_session
        {"cls": "ScenarioB", "meth": "fixture_session", "part": "teardown"},
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

    expected_data_2 = (
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
        # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
        {"cls": "ScenarioA", "meth": "fixture_session", "part": "construction"},

        # stops execution here (only valid if the ScenarioB fixture was called first)
        # {"cls": "ScenarioA", "meth": "fixture_session", "part": "teardown"},
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
    error1 = None
    try:
        compare_observed_list_with_expected(exec_list, expected_data_1)
    except AssertionError as exc:
        error1 = exc
    error2 = None
    try:
        compare_observed_list_with_expected(exec_list, expected_data_2)
    except AssertionError as exc:
        error2 = exc
    if error1 and error2:
        # can not find possible matching
        raise error1

    # check result states everywhere (have to be SUCCESS everywhere
    assert session.executor_tree.executor_result == ResultState.ERROR, "test session does not terminates with ERROR"

    assert session.executor_tree.construct_result.result == ResultState.ERROR, \
        "global executor tree construct part does not set ResultState.ERROR"
    assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
        "global executor tree body part does not set ResultState.NOT_RUN"
    assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
        "global executor tree teardown part does not set ResultState.SUCCESS"
    for cur_setup_executor in session.executor_tree.setup_executors:
        assert cur_setup_executor.executor_result == ResultState.NOT_RUN, \
            "the setup executor does not have result NOT_RUN"

        assert cur_setup_executor.construct_result.result == ResultState.NOT_RUN
        assert cur_setup_executor.body_result.result == ResultState.NOT_RUN
        assert cur_setup_executor.teardown_result.result == ResultState.NOT_RUN

        for cur_scenario_executor in cur_setup_executor.scenario_executors:
            assert cur_scenario_executor.executor_result == ResultState.NOT_RUN, \
                "the scenario executor does not have result NOT_RUN"

            assert cur_scenario_executor.construct_result.result == ResultState.NOT_RUN
            assert cur_scenario_executor.body_result.result == ResultState.NOT_RUN
            assert cur_scenario_executor.teardown_result.result == ResultState.NOT_RUN

            for cur_variation_executor in cur_scenario_executor.variation_executors:
                assert cur_variation_executor.executor_result == ResultState.NOT_RUN, \
                    "the variation executor does not have result NOT_RUN"

                assert cur_variation_executor.construct_result.result == ResultState.NOT_RUN
                assert cur_variation_executor.body_result.result == ResultState.NOT_RUN
                assert cur_variation_executor.teardown_result.result == ResultState.NOT_RUN

                for cur_testcase_executor in cur_variation_executor.testcase_executors:
                    assert cur_testcase_executor.executor_result == ResultState.NOT_RUN, \
                        "the testcase executor does not have result NOT_RUN"

                    assert cur_testcase_executor.construct_result.result == ResultState.NOT_RUN
                    assert cur_testcase_executor.body_result.result == ResultState.NOT_RUN
                    assert cur_testcase_executor.teardown_result.result == ResultState.NOT_RUN
