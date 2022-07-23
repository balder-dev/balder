import pathlib
import sys

from multiprocessing import Process
from _balder.balder_session import BalderSession
from _balder.exceptions import IllegalVDeviceMappingError

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_vdevice_mapping_in_vdevice_feature_scenario(balder_working_dir):
    """
    This testcase executes the basic example and checks if the tree ends with the result SUCCESS. This environment has
    one special usage of a vDevice in scenario based feature ``FeatureII``. A feature of this vDevice has an own mapping
    to another vDevice. vDevice-Mappings for features inside vDevices are not allowed! Balder should throw an error on
    collecting level.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    exception = None
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    try:
        session.run()
    except Exception as exc:
        exception = exc
    print("\n")

    # get the class instance from already imported module - balder loads it from given working directory
    RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
    runtime_data = RuntimeObserver.data.copy()

    exec_list = []
    for cur_data in runtime_data:
        new_data = cur_data.copy()
        new_data["file"] = pathlib.Path(new_data["file"]).relative_to(env_dir)
        exec_list.append(new_data)

    expected_data = (

    )

    compare_observed_list_with_expected(exec_list, expected_data)

    assert isinstance(exception, IllegalVDeviceMappingError), \
        f"receive a exception type that was not expected (expected `{IllegalVDeviceMappingError.__name__}`): " \
        f"{str(exception)}"

    # check result states everywhere (have to be SUCCESS everywhere
    assert session.executor_tree is None, \
        "test session has a executor_tree object - should not be possible if error was already be detected on " \
        "constructor level (as expected)"
