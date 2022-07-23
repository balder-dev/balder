import pathlib
import sys

from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected


def test_0_exactly_one_less_feature_in_setup(balder_working_dir):
    """
    This testcase uses a reduced version of the basic envtester environment. It should have no matching between the
    ``ScenarioA`` and the ``SetupA`` because the ``SetupDevice1`` does not provide an implementation of ``FeatureIII``.
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

    # get the class instance from already imported module - balder loads it from given working directory
    RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
    runtime_data = RuntimeObserver.data.copy()

    exec_list = []
    for cur_data in runtime_data:
        new_data = cur_data.copy()
        new_data["file"] = pathlib.Path(new_data["file"]).relative_to(env_dir)
        exec_list.append(new_data)

    # empty, because the test session should not run
    expected_data = (
    )

    compare_observed_list_with_expected(exec_list, expected_data)

    # check result states everywhere (have to be SUCCESS everywhere
    assert session.executor_tree.executor_result == ResultState.NOT_RUN, "test session does not terminates with NOT_RUN"

    assert session.executor_tree.construct_result.result == ResultState.NOT_RUN, \
        "global executor tree construct part does not set ResultState.NOT_RUN"
    assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
        "global executor tree body part does not set ResultState.SUCCESS"
    assert session.executor_tree.teardown_result.result == ResultState.NOT_RUN, \
        "global executor tree teardown part does not set ResultState.NOT_RUN"
