import pathlib
import sys

from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_unclear_setup_scoped_fixture_reference(balder_working_dir):
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
    proc = Process(target=processed, args=(balder_working_dir,))
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

    compare_observed_list_with_expected(exec_list, expected_data)

    # check result states everywhere (have to be SUCCESS everywhere
    assert session.executor_tree.executor_result == ResultState.ERROR, \
        "test session does not terminates with an ERROR state"

    assert session.executor_tree.construct_result.result == ResultState.ERROR, \
        "global executor tree construct part does not set ResultState.SUCCESS"
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
                    "the variation executor does not have result SUCCESS"

                assert cur_variation_executor.construct_result.result == ResultState.NOT_RUN
                assert cur_variation_executor.body_result.result == ResultState.NOT_RUN
                assert cur_variation_executor.teardown_result.result == ResultState.NOT_RUN

                for cur_testcase_executor in cur_variation_executor.testcase_executors:
                    assert cur_testcase_executor.executor_result == ResultState.NOT_RUN, \
                        "the testcase executor does not have result SUCCESS"

                    assert cur_testcase_executor.construct_result.result == ResultState.NOT_RUN
                    assert cur_testcase_executor.body_result.result == ResultState.NOT_RUN
                    assert cur_testcase_executor.teardown_result.result == ResultState.NOT_RUN
