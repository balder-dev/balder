import logging
import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber
from balder.exceptions import AccessToUnmappedVDeviceException

logger = logging.getLogger(__name__)


class SetupPythonAddVDevice2WithTwoMapped(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate(ANumberProviderDevice2="NumberProviderTwo")

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProviderOne(balder.Device):
        n = PyAddProvideANumber()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProviderTwo(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []

    def validate_vdevice_references(self):
        assert isinstance(self.Calculator.calc.get_number_of_provider_2(), int), \
            f"the currently mapped internal vdevice returns an unexpected value " \
            f"`{self.Calculator.calc.get_number_of_provider_2()}`"

        try:
            self.Calculator.calc.get_number_of_provider_1()
            assert False, "provider 1 does return a value -> not allowed, because this VDevice was not mapped"
        except AccessToUnmappedVDeviceException as exc:
            logger.info(f'access to unmapped VDevice throws error message: `{str(exc)}`')
            assert exc.args[0] == "it is not allowed to access the attributes of an unmapped VDevice - " \
                                  "did you forget to map it?"

    @balder.fixture(level='variation')
    def fixture_vdevice_access_variation(self):
        self.validate_vdevice_references()
        yield
        self.validate_vdevice_references()

    @balder.fixture(level='testcase')
    def fixture_vdevice_access_testcase(self):
        self.validate_vdevice_references()
        yield
        self.validate_vdevice_references()
