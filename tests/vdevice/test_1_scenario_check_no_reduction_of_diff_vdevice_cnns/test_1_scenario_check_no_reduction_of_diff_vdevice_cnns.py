from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_scenario_check_no_reduction_of_diff_vdevice_cnns(balder_working_dir):
    """
    This testcase executes an expanded version of the CALCULATOR environment.

    It defines three new features ``VDeviceHelperFeature1``, ``VDeviceHelperFeature2`` and ``VDeviceHelperFeature3``
    that are all used by the ``ScenarioAdding.NumberOneDevice`` and the ``SetupPythonAdd.NumberProvider1``.
    Every of these features has a VDevice that reduces the connection tree:

    * ``VDeviceHelperFeature1``: ``SimulatedChildConnection.based_on(SimulatedParentConnection)``
    * ``VDeviceHelperFeature2``: ``SimulatedChildConnection``
    * ``VDeviceHelperFeature3``: ``MySimplySharedMemoryConnection``

    The VDevices are mapped on scenario level here!

    The devices (both scenario and setup) have a connection
    ``SimulatedChildConnection.based_on(SimulatedParentConnection) AND MySimplySharedMemoryConnection``, that should
    work with the different mapped VDevice requirements of these features.

    The test should run successfully with exactly one variation (these features are only provided for one ``Number*``
    device).
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
    assert len(session.executor_tree.get_setup_executors()[0].get_scenario_executors()) == 1, \
        "not exactly one scenario executor found"

    scenario_executors = session.executor_tree.get_setup_executors()[0].get_scenario_executors()
    assert scenario_executors[0].base_scenario_class.__class__.__name__ == \
           "ScenarioAdding", "wrong scenario class was executed"
    assert len(scenario_executors[0].get_variation_executors()) == 1, \
        "not exactly two variation executor found"
