from _balder.balder_session import BalderSession
from _balder.exceptions import BalderException, DeviceOverwritingError

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ScenarioInheritanceMissingDeviceInheritance(Base0EnvtesterClass):
    """
    This testcase executes a reduced version of the basic envtester environment. It only implements the `ScenarioA` and
    its related `SetupA` and a child class of the related ScenarioA that has an additional test method.

    The child class define both devices, but inherits only from one device correctly.

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
        assert exc.args[0] == "the inner device class `ScenarioAChild.ScenarioDevice2` has the same name than the " \
                              "device `ScenarioAParent.ScenarioDevice2` - it should also inherit from it"

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree is None, "test session does not terminates before collector work was done"
