from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_scenario_inheritance_use_parent_connections(balder_working_dir):
    """
    This testcase executes the general CALCULATOR example.

    It has two inherited scenarios, while only the parent scenario defines some connections. The environment uses two
    setups - one without connections (would match with child scenario if no parent would exist) and one with the
    required connections, that are only defined in parent scenario class.

    The test validates, that only the correct setup (with connection) will be executed with the child scenario class.
    This secures that the parent connection will be inherited correctly.
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
        "not exactly one setup executor found"
    assert session.executor_tree.get_setup_executors()[0].base_setup_class.__class__.__name__ == \
           "SetupPythonAdd", "wrong scenario class was executed"

    scenario_executors = session.executor_tree.get_setup_executors()[0].get_scenario_executors()

    assert len(scenario_executors) == 1, "not exactly one scenario executor found"
    assert scenario_executors[0].base_scenario_class.__class__.__name__ == "ScenarioAddingChild", \
        "wrong scenario class was executed"
    assert len(scenario_executors[0].get_variation_executors()) == 2, "not exactly two variation executor found"
