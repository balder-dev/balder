from multiprocessing import Process

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession


def test_1_illegal_non_testmethod_decorated(balder_working_dir):
    """
    This testcase executes the basic example but decorated a non-testmethod with the `covered_by` decorator. The test
    expects an error message.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def check_error_of_exc(exc: BaseException):
    assert isinstance(exc, TypeError)
    assert exc.args[0] == ("the use of the `@covered_by` decorator is only allowed for test methods of "
                                     "`Scenario` objects - the method `ScenarioAdding.normal_method` does not "
                                     "start with `test_` and is not a valid test method")

def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    try:
        session.run()
        print("\n")
        assert False, "test session terminates without an error"
    except RuntimeError as exc:
        assert exc.args[0] == ("Error calling __set_name__ on 'CoveredByDecorator' instance 'normal_method' in "
                               "'ScenarioAdding'")
        check_error_of_exc(exc.__cause__)
    except TypeError as exc:
        check_error_of_exc(exc)

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
