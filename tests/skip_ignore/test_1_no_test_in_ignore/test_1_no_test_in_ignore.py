from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_calculator(balder_working_dir):
    """
    This testcase executes the basic example, while the scenario defines a raw method instead of a test method in its
    IGNORE marker. It is expected, that the executor tree does not run and balder terminates with an excepted exception.
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
        assert exc.args[0] == ("the attribute `do_something_but_be_not_a_test` mentioned in IGNORE list of scenario "
                               "`<class 'env.scenarios.scenario_adding.ScenarioAdding'>` is no valid test method and "
                               "can not be used here")

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
