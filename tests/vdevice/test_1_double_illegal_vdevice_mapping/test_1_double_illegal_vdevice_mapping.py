from multiprocessing import Process

from _balder.balder_session import BalderSession
from _balder.testresult import ResultState


def test_1_double_illegal_vdevice_mapping(balder_working_dir):
    """
    This testcase executes the basic example and checks that the session terminates without errors and that the
    variation will not be executed.

    The test is the expanded version of the basic calculator example. Its feature `ProvidesANumberFeature` has two
    additional VDevice classes that are both mapped but on different levels (one is correctly mapped on scenario level
    and one on setup level). This is allowed, but leads to the not-executing of the variation.
    To map another vDevice this test devices an additional not connected scenario device `DoNothingDevice`.
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

    assert session.executor_tree.construct_result.result == ResultState.NOT_RUN, \
            "global executor tree construct part does not set ResultState.NOT_RUN"
    assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
        "global executor tree body part does not set ResultState.NOT_RUN"
    assert session.executor_tree.teardown_result.result == ResultState.NOT_RUN, \
        "global executor tree teardown part does not set ResultState.NOT_RUN"

    assert len(session.executor_tree.get_setup_executors()) == 0, \
        "there exists some setup executor - that should not be the case"
