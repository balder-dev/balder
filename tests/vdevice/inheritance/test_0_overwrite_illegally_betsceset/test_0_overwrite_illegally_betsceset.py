from multiprocessing import Process
from _balder.balder_session import BalderSession
from _balder.exceptions import VDeviceOverwritingError


def test_0_overwrite_illegally_betsceset(balder_working_dir):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BETWEEN the
    scenario-feature and the setup-feature.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices, which is directly instantiated in the
    scenario. This feature will be overwritten by a direct child `FeatureOfRelevanceLvl2` that overwrites both vDevices.
    Instead, of made as in the test `test_0_overwrite_correctly_betsceset`, not all vDevices are being overwritten here.
    The setup device instantiates a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    The test should terminate successful and no error should occur!
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
    except VDeviceOverwritingError as exc:
        assert exc.args[0] == "missing overwriting of parent VDevice class `FeatureOfRelevanceLvl1.VDeviceWithII` in " \
                              "feature class `FeatureOfRelevanceLvl2` - if you overwrite one or more VDevice(s) you " \
                              "have to overwrite all!"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
