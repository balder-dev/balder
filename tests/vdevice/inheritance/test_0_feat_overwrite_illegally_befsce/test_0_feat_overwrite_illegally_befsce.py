from _balder.balder_session import BalderSession
from _balder.exceptions import FeatureOverwritingError, BalderException

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0FeatOverwriteIllegallyBefsce(Base0EnvtesterClass):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BEFORE the feature
    is being instantiated in a SCENARIO.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices. This feature will be overwritten by the
    direct child `FeatureOfRelevanceLvl2`, that will be used in our scenario and also be mapped to a vDevice.
    Of course the setup device also implements a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    It tries to overwrite a feature of the active vDevice from `FeatureOfRelevanceLvl2` with a class that is not allowed
    here (no direct child of overwritten one).

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
        assert isinstance(exc, FeatureOverwritingError), 'unexpected error type'
        assert exc.args[0] == "you are trying to overwrite an existing vDevice Feature property `i` in vDevice " \
                              "`FeatureOfRelevanceLvl2.VDeviceWithI` from the parent vDevice class " \
                              "`FeatureOfRelevanceLvl1.VDeviceWithI` - this is only possible with a child (or with " \
                              "the same) feature class the parent uses (in this case the `IllegalFeature`)"

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree is None, "test session does not terminates before collector work was done"
