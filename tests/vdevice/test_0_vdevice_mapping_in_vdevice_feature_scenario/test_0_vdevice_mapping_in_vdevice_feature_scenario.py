from _balder.balder_session import BalderSession
from _balder.exceptions import IllegalVDeviceMappingError, BalderException

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0VdeviceMappingInVdeviceFeatureScenario(Base0EnvtesterClass):
    """
    This testcase executes the basic example and checks if the tree ends with the result SUCCESS. This environment has
    one special usage of a vDevice in scenario based feature ``FeatureII``. A feature of this vDevice has an own mapping
    to another vDevice. vDevice-Mappings for features inside vDevices are not allowed! Balder should throw an error on
    collecting level.
    """

    @property
    def expected_data(self) -> tuple:
        return ()

    @property
    def expected_exit_code(self):
        return 4

    @staticmethod
    def handle_balder_exception(exc: BalderException):
        assert isinstance(exc, IllegalVDeviceMappingError), \
            f"receive a exception type that was not expected (expected `{IllegalVDeviceMappingError.__name__}`): " \
            f"{str(exc)}"
        assert exc.args[0] == 'the feature `FeatureI` you have instantiated in your vDevice `OtherVDevice1` of ' \
                              'feature `FeatureII` has a own vDevice mapping - vDevice mappings are allowed for ' \
                              'features on Devices only'

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere
        assert session.executor_tree is None, \
            "test session has a executor_tree object - should not be possible if error was already be detected on " \
            "constructor level (as expected)"
