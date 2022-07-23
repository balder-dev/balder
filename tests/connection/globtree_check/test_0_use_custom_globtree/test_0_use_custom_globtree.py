import traceback
from multiprocessing import Process
from _balder.balder_session import BalderSession
from balder.exceptions import IllegalConnectionTypeError


def test_0_use_custom_globtree(balder_working_dir):
    """
    This test tries to use a custom glob-tree, which is defined in the `BalderSettings` of the related environment. The
    test will be executed with some connections from the normal conn-tree. Balder has to throw an error, because all used
    connection are unknown for the newly created active conn-tree.
    """
    proc = Process(target=processed, args=(balder_working_dir,))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    exception = None
    try:
        session.run()
        print("\n")
    except IllegalConnectionTypeError as exc:
        traceback.print_exc()
        exception = exc
    assert exception, "no exception was thrown"
