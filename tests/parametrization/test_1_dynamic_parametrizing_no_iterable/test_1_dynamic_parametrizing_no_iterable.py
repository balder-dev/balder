from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from _balder.executor.unresolved_parametrized_testcase_executor import UnresolvedParametrizedTestcaseExecutor


def test_1_calculator(balder_working_dir):
    """
    This testcase executes the basic example and checks if the tree ends with the result SUCCESS
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    session.run()

    assert session.executor_tree.executor_result == ResultState.ERROR, \
        "test session does not terminates with success"

    assert session.executor_tree.construct_result.result == ResultState.SUCCESS, \
        "global executor tree construct part does not set ResultState.SUCCESS"
    assert session.executor_tree.body_result.result == ResultState.ERROR, \
        "global executor tree body part does not set ResultState.FAILURE"
    assert session.executor_tree.teardown_result.result == ResultState.NOT_RUN, \
        "global executor tree teardown part does not set ResultState.NOT_RUN"

    all_setup_executor = session.executor_tree.get_setup_executors()
    assert len(all_setup_executor) == 1, f"detect more than one setup executor"

    assert all_setup_executor[0].executor_result == ResultState.ERROR, \
        "the setup executor does not have result SUCCESS"

    assert all_setup_executor[0].construct_result.result == ResultState.SUCCESS
    assert all_setup_executor[0].body_result.result == ResultState.ERROR
    assert all_setup_executor[0].teardown_result.result == ResultState.NOT_RUN

    all_scenario_executor = all_setup_executor[0].get_scenario_executors()
    assert len(all_scenario_executor) == 1, f"detect more than one scenario executor"

    assert all_scenario_executor[0].executor_result == ResultState.ERROR, \
        "the scenario executor does not have result SUCCESS"

    assert all_scenario_executor[0].construct_result.result == ResultState.ERROR
    assert all_scenario_executor[0].body_result.result == ResultState.NOT_RUN
    assert all_scenario_executor[0].teardown_result.result == ResultState.NOT_RUN

    all_variation_executor = all_scenario_executor[0].get_variation_executors()

    assert len(all_variation_executor) == 1, f"detect more than one variation executor"

    assert all_variation_executor[0].executor_result == ResultState.NOT_RUN, \
        "the variation executor does not have result SUCCESS"

    assert all_variation_executor[0].construct_result.result == ResultState.NOT_RUN
    assert all_variation_executor[0].body_result.result == ResultState.NOT_RUN
    assert all_variation_executor[0].teardown_result.result == ResultState.NOT_RUN

    all_testcase_executor = all_variation_executor[0].get_testcase_executors()
    assert len(all_testcase_executor) == 1, f"detect some testcase executor"
    assert isinstance(all_testcase_executor[0], UnresolvedParametrizedTestcaseExecutor), \
        f"test case executor is from unexpected type {type(all_testcase_executor[0])}"

    assert all_testcase_executor[0].construct_result.result == ResultState.NOT_RUN
    assert all_testcase_executor[0].body_result.result == ResultState.NOT_RUN
    assert all_testcase_executor[0].teardown_result.result == ResultState.NOT_RUN

    exceptions = all_scenario_executor[0].get_all_recognized_exception()
    assert len(exceptions) == 1, f"detect more than one exception executor"
    assert exceptions[0].args[0] == ("feature parametrizing not possible, because "
                                     "`ScenarioAdding.NumberOneDevice.example.get_random_numbers` does not return "
                                     "Iterable")


