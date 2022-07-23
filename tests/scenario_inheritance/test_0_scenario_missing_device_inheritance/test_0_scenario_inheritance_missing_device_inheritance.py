
from multiprocessing import Process
from balder.exceptions import DeviceOverwritingError
from _balder.balder_session import BalderSession


def test_0_scenario_inheritance_missing_device_inheritance(balder_working_dir):
    """
    This testcase executes a reduced version of the basic envtester environment. It only implements the `ScenarioA` and
    its related `SetupA` and a child class of the related ScenarioA that has an additional test method.

    The child class define both devices, but inherits only from one device correctly.

    .. note::
        The `ScenarioAParent` class has a child (the `ScenarioAChild` class). This forbids the execution of the
        `ScenarioAParent` class.
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
    except DeviceOverwritingError as exc:
        assert exc.args[0] == "the inner device class `ScenarioAChild.ScenarioDevice2` has the same name than the " \
                              "device `ScenarioAParent.ScenarioDevice2` - it should also inherit from it"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
