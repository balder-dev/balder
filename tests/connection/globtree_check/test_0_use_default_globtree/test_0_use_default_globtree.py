from multiprocessing import Process
from _balder.balder_session import BalderSession
from _balder.testresult import ResultState


def test_0_use_default_globtree(balder_working_dir):
    """
    This tests secures that the default globtree is used if there is no special setting done in project's
    `BalderSettings` object.
    """
    proc = Process(target=processed, args=(balder_working_dir,))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):

    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    session.run()
    print("\n")

    # check result states everywhere (have to be SUCCESS everywhere)
    assert session.executor_tree.executor_result == ResultState.SUCCESS, "test session does not terminates with SUCCESS"
    # check that there are all expected mappings
    assert len(session.executor_tree.get_all_testcase_executors()) == 4, "do not resolve to exactly 4 testcases"
