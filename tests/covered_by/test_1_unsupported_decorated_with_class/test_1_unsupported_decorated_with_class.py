from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_calculator(balder_working_dir):
    """
    This testcase executes the basic example by using the `covered_by()` decorator with a scenario class. This is
    currently not supported, the test checks that an expected error message is thrown.
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
    except NotImplementedError as exc:
        assert exc.args[0] == "The covered-by other scenario classes is not supported yet"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
