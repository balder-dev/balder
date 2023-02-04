from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_unmapped_vdevice_access(balder_working_dir):
    """
    This is a modified version of the simple calculator environment. This specialized environment has two VDevices
    :class:`ANumberProviderDevice1` and :class:`ANumberProviderDevice2` inside the ``lib.feature.AddCalculateFeature``,
    which are mapped in different constellations inside the scenarios and setups.

    There are tests and fixtures (variation and testcase level only) that secures that the
    `AccessToUnmappedVDeviceException` are thrown if the test/fixture tries to access a VDevice which is not mapped. It
    also validates that the features of the mapped VDevice can be accessed and returns the expected data.
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
