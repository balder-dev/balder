from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_devicemethod(balder_working_dir):
    """
    This testcase validates an environment with a Scenario-Device that has an own method. It will be checked if the
    method code uses the assigned Setup-Features correctly.

    The test tries a class method and a static method. It fails if one of the methods raises a NotImplementedError.
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
