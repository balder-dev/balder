from multiprocessing import Process
from _balder.balder_session import BalderSession
from _balder.exceptions import VDeviceOverwritingError


def test_0_overwrite_illegally_miss_inherit_befsce(balder_working_dir):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BEFORE the feature
    is being instantiated in a SCENARIO.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices. This feature will be overwritten by the
    direct child `FeatureOfRelevanceLvl2`, that will be used in our scenario and also be mapped to a vDevice. Instead,
    of made as in the test `test_0_overwrite_correctly_befsce`, the inheritance is missing for one vDevices here.
    Of course the setup device also implements a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    The test should fail on collector level, because overwritten vDevices with the same name have to inherit from
    itself too.
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
        assert exc.args[0] == "the inner vDevice class `FeatureOfRelevanceLvl2.VDeviceWithI` has the same name than " \
                              "the vDevice `FeatureOfRelevanceLvl1.VDeviceWithI` - it should also inherit from it"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
