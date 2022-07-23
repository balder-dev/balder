
from multiprocessing import Process
from balder.exceptions import DeviceOverwritingError
from _balder.balder_session import BalderSession


def test_0_scenario_inheritance_overwrite_only_one_device(balder_working_dir):
    """
    This testcase executes a reduced version of the basic envtester environment. It only implements the `ScenarioA` and
    its related `SetupA` and a child class of the related ScenarioA that has an additional test method.

    The child class DOES ONLY overwrite one device instead of two. This should be forbidden. The collector should throw
    an exception.

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
        assert exc.args[0] == "found a device `ScenarioAParent.ScenarioDevice2` which is part of a parent class, " \
                              "but it is not implemented in child class `ScenarioAChild`"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
