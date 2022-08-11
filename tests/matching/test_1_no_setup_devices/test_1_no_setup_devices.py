from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_no_setup_devices(balder_working_dir):
    """
    This testcase executes the CALCULATOR environment in a modified version. In this version the setup has no devices.
    Balder should run successful, but no variation should be found.

    This test secures that Balder terminates successful, but without a possible variation.
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

    assert session.executor_tree.executor_result == ResultState.NOT_RUN, \
        "test session does not terminates with result NOT_RUN"

    assert len(session.executor_tree.all_child_executors) == 0, "the executor tree is not empty"
