from multiprocessing import Process

from _balder.balder_session import BalderSession


def test_1_covered_by_non_testmethod(balder_working_dir):
    """
    This testcase executes the basic example but uses a `covered_by` decorator with a non-testmethod.
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
    except TypeError as exc:
        assert exc.args[0] == ("the given element for `item` must be a test method of a scenario class (has to start "
                               "with `test_`)")

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
