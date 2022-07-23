from multiprocessing import Process
from _balder.balder_session import BalderSession
from _balder.exceptions import FeatureOverwritingError


def test_0_feat_overwrite_illegally_befsce(balder_working_dir):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BEFORE the feature
    is being instantiated in a SCENARIO.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices. This feature will be overwritten by the
    direct child `FeatureOfRelevanceLvl2`, that will be used in our scenario and also be mapped to a vDevice.
    Of course the setup device also implements a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    It tries to overwrite a feature of the active vDevice from `FeatureOfRelevanceLvl2` with a class that is not allowed
    here (no direct child of overwritten one).

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
    except FeatureOverwritingError as exc:
        assert exc.args[0] == "you are trying to overwrite an existing vDevice Feature property `i` in vDevice " \
                              "`FeatureOfRelevanceLvl2.VDeviceWithI` from the parent vDevice class " \
                              "`FeatureOfRelevanceLvl1.VDeviceWithI` - this is only possible with a child (or with " \
                              "the same) feature class the parent uses (in this case the `IllegalFeature`)"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
