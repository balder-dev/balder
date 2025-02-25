from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_calculator(balder_working_dir):
    """
    This testcase executes the basic example but with two Scenarios. The parent scenario adds the test method to the
    marker IGNORE, while the child scenario adds the test method to the marker SKIP. This should throw an error on
    collecting level.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    try:
        session.run()
        print("\n")
        assert False, "test session terminates without an error"
    except ValueError as exc:
        assert exc.args[0] == ("the element `test_add_two_numbers` given at class attribute `ScenarioAddingChild.SKIP` "
                               "was already added to IGNORE in a higher parent class - not possible to add it now "
                               "to SKIP")

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
