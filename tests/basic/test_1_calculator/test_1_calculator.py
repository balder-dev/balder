from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


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
    print("\n")

    assert session.executor_tree.executor_result == ResultState.SUCCESS, \
        "test session does not terminates with success"
