from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_vdevice_which_is_no_part_of_a_variation(balder_working_dir):
    """
    This testcase is a modified version of the calculator environment.

    The setup defines two calculator devices `Calculator1` and `Calculator2` that theoretically could map to the
    scenario device `Calculator`. Normally both of these setup devices `Calculator1` and `Calculator2` should map.

    However, since we have a VDevice mapping on setup level only to the `Calculator1` device, balder should not allow
    the second variation, at which the `Calculator2` would be mapped to the scenario device `Calculator`, because it
    cannot be used as VDevice.

    The test secures that only the mapped `Calculator1` is a valid variation.
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
    for cur_variation_executor in scenario_executors[0].get_variation_executors():
        all_setup_devices = [cur_device.__name__ for cur_device in cur_variation_executor.base_device_mapping.values()]
        assert "Calculator1" in all_setup_devices, \
            "can not find the expected `Calculator` setup device in mapped-devices"
        assert "Calculator2" not in all_setup_devices, \
            "`Calculator2` should not be contained in mapped-devices"
