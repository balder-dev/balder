from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_reverse_routing(balder_working_dir):
    """
    This testcase has an environment, that should be able to be executed in two possible variations. The only key
    difference to the basic env `test_calculator` is the reverse `@connect(..)` marker. In scenario, the provider devices
    are decorated. In setup, the calculator device is decorated with both `@connect(..)` marker
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
