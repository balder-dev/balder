from multiprocessing import Process

from _balder.balder_session import BalderSession


def test_1_duplicate_vdevice_mapping(balder_working_dir):
    """
    This testcase executes the basic example and checks that the collector throws an error and the tree will not be
    created.

    The test is the expanded version of the basic calculator example. Its feature `ProvidesANumberFeature` has two
    additional VDevice classes that are both mapped here in this version (in same constructor). This is not allowed.
    This test expects that balder will throw an exception for this.
    To map another vDevice this test devices an additional not connected device `DoNothingDevice`.

    The test expects, that balder throws an error, because the VDevice mapping is not done correctly.
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
        assert False, "the expected `AttributeError` exception was not being thrown"
    except AttributeError as exc:
        assert exc.args[0] == "the constructor expects exactly none or one vDevice mapping - found more than one here"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
