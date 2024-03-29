from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_2_msg_transmission(balder_working_dir):
    """
    This testcase executes the basic example for transmitting a message between two devices. It checks that the
    Balder process terminates with exit code 0.

    This environment provides one single scenario that consists of one Device which implements the feature
    :class:`SendMessageFeature` and one Device which implements the feature :class:`ReceiveMessageFeature`. It holds
    two different feature implementations, while the
    :class:`SendOverLocalVarFeature`/:class:`ReceiveOverLocalVarFeature` transmits the message over a local internal
    variable inside the receive-feature and the :class:`SendOverQueueFeature`/:class:`ReceiveOverQueueFeature` uses a
    queue between these two features to transmit the message.
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
