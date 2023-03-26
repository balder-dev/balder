from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_reverse_connect_3_scen_4_setup_devs(balder_working_dir):
    """
    This testcase uses the calculator environment in a modified version. It gets an additional `NumberProvider3` on
    setup level. On setup level all connections are defined over the `Calculator` (the connections are defined reverse).

    The test validates that the session terminates successfully and all three variations were executed.
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
    assert len(session.executor_tree.get_setup_executors()) == 1, \
        "found not exactly one setup executor"

    scenario_executors = session.executor_tree.get_setup_executors()[0].get_scenario_executors()

    assert len(scenario_executors) == 1, \
        "found not exactly one scenario executor"
    assert len(scenario_executors[0].get_variation_executors()) == 6, \
        "found not exactly three variation executor"
