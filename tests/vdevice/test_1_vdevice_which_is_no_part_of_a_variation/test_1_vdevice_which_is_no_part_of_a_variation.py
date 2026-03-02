from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_vdevice_which_is_no_part_of_a_variation(balder_working_dir):
    """
    This testcase is a modified version of the calculator environment.

    The setup defines two an additional helper devices `HelperDevice` that is never a part of the variation (does not
    have a mapped scenario-device). It is expected, that the variation is executed and the VDevice is mapped.
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
    assert len(session.executor_tree.get_setup_executors()) == 1

    scenario_executors = session.executor_tree.get_setup_executors()[0].get_scenario_executors()
    assert len(scenario_executors) == 1
    assert len(scenario_executors[0].get_variation_executors()) == 2
