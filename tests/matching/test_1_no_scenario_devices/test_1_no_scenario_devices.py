from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_no_scenario_devices(balder_working_dir):
    """
    This testcase uses the CALCULATOR environment in a modified version. For this test, the scenario does not define any
    devices.

    The test secures that the setup will still be executed.
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

    assert session.executor_tree.executor_result == ResultState.SUCCESS, \
        "test session does not terminates with success"
    assert len(session.executor_tree.all_child_executors) == 1, "found not exactly one matching setup"
    setup_executor = session.executor_tree.get_setup_executors()[0]
    assert setup_executor.base_setup_class.__class__.__name__ == "SetupPythonAdd", "unexpected matching setup"
    assert len(setup_executor.get_scenario_executors()) == 1, "found not exactly one matching scenario"
    scenario_executor = setup_executor.get_scenario_executors()[0]
    assert scenario_executor.base_scenario_class.__class__.__name__ == "ScenarioAdding", "unexpected matching scenario"
    assert len(scenario_executor.get_variation_executors()) == 1, "found not exactly one matching scenario"
