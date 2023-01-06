from balder.exceptions import DeviceOverwritingError, BalderException
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ScenarioInheritanceOverwriteOnlyOneDevice(Base0EnvtesterClass):
    """
    This testcase executes a reduced version of the basic envtester environment. It only implements the `ScenarioA` and
    its related `SetupA` and a child class of the related ScenarioA that has an additional test method.

    The child class DOES ONLY overwrite one device instead of two. This should be forbidden. The collector should throw
    an exception.

    .. note::
        The `ScenarioAParent` class has a child (the `ScenarioAChild` class). This forbids the execution of the
        `ScenarioAParent` class.
    """
    @property
    def expected_data(self) -> tuple:
        return ()

    @property
    def expected_exit_code(self) -> int:
        return 4

    @staticmethod
    def handle_balder_exception(exc: BalderException):
        assert isinstance(exc, DeviceOverwritingError), 'unexpected exception type'
        assert exc.args[0] == "found a device `ScenarioAParent.ScenarioDevice2` which is part of a parent class, " \
                              "but it is not implemented in child class `ScenarioAChild`"

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree is None, "test session does not terminates before collector work was done"

