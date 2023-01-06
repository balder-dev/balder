from _balder.balder_session import BalderSession
from _balder.exceptions import VDeviceOverwritingError, BalderException

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0OverwriteIllegallyMissInheritBetsceset(Base0EnvtesterClass):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BETWEEN the
    scenario-feature and the setup-feature.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices, which is directly instantiated in the
    scenario. This feature will be overwritten by a direct child `FeatureOfRelevanceLvl2` that overwrites both vDevices.
    Instead, of made as in the test `test_0_overwrite_correctly_betsceset`, for one overwritten vDevices the inheritance
    is missing here.
    The setup device instantiates a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    The test should terminate successful and no error should occur!
    """

    @property
    def expected_data(self) -> tuple:
        return ()

    @property
    def expected_exit_code(self) -> int:
        return 4

    @staticmethod
    def handle_balder_exception(exc: BalderException):
        assert isinstance(exc, VDeviceOverwritingError), 'unexpected exception type'
        assert exc.args[0] == "the inner vDevice class `FeatureOfRelevanceLvl2.VDeviceWithI` has the same name than " \
                              "the vDevice `FeatureOfRelevanceLvl1.VDeviceWithI` - it should also inherit from it"

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree is None, "test session does not terminates before collector work was done"
