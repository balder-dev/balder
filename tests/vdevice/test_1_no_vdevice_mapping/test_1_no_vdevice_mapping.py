from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_no_vdevice_mapping(balder_working_dir):
    """
    This testcase executes the basic example and checks if the tree ends in the state NOT_RUN. All variations should not
    be executed, because there is a different vDevice mapping in scenario and in setup.

    The test is the expanded version of the basic calculator example. Its feature `ProvidesANumberFeature` has an
    additional VDevice that is not mapped here in this version.

    The test expects, that balder terminates without executing one test.
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
        "test session does not terminates with error"
    assert len(session.executor_tree.all_child_executors) == 0, "found not expected child elements in the tree"
