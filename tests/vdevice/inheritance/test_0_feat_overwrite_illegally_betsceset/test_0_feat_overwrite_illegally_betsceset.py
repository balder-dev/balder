from _balder.balder_session import BalderSession
from _balder.exceptions import FeatureOverwritingError, BalderException

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0FeatOverwriteIllegallyBetsceset(Base0EnvtesterClass):
    """
    This testcase is a modified version of the basic ENVTESTER environment. It is limited to the `ScenarioA` and the
    `SetupA` and uses a feature `FeatureOfRelevance` for testing the correct overwriting of VDevices BETWEEN the
    scenario-feature and the setup-feature.

    This test defines a new feature `FeatureOfRelevanceLvl1` with two vDevices, which is directly instantiated in the
    scenario. This feature will be overwritten by a direct child `FeatureOfRelevanceLvl2` that overwrites both vDevices.
    The setup device instantiates a child class (`SetupFeatureOfRelevanceLvl3`) of it.

    It tries to overwrite a feature of the active vDevice from `SetupFeatureOfRelevanceLvl3` with a class that is not
    allowed here (no direct child of overwritten one).

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
        assert isinstance(exc, FeatureOverwritingError), "wrong exception type"
        assert exc.args[0] == "you are trying to overwrite an existing vDevice Feature property `i` in vDevice " \
                              "`FeatureOfRelevanceLvl2.VDeviceWithI` from the parent vDevice class " \
                              "`FeatureOfRelevanceLvl1.VDeviceWithI` - this is only possible with a child (or with " \
                              "the same) feature class the parent uses (in this case the `FeatureI`)"

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree is None, "test session does not terminates before collector work was done"
