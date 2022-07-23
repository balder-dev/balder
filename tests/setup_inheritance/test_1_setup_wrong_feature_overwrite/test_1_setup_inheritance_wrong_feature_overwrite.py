from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from balder.exceptions import FeatureOverwritingError


def test_1_setup_inheritance_wrong_feature_overwrite(balder_working_dir):
    """
    This testcase executes the calculator environment, but uses a special child setup class that overwrites a feature
    property of an inherited device which uses a complete independent feature. This is not allowed and should result in
    a collector error.
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
        assert exc.args[0] == "the feature `PyAddCalculate` with the attribute name `calc` of the device " \
                              "`Calculator` you are trying to overwrite is no child class of the feature " \
                              "`IllegalFeature` that was assigned to this property before"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
