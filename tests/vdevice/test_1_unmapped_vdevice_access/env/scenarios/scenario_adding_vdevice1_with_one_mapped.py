import logging
import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature
from balder.exceptions import AccessToUnmappedVDeviceException


logger = logging.getLogger(__name__)


class ScenarioAddingVDevice1WithOneMapped(balder.Scenario):

    class Calculator(balder.Device):
        adds = AddCalculateFeature(ANumberProviderDevice1="NumberOneDevice")

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberTwoDevice(balder.Device):
        number = ProvidesANumberFeature()

    def test_add_two_numbers(self):
        self.NumberOneDevice.number.set_number(3)
        self.NumberTwoDevice.number.set_number(4)

        self.NumberOneDevice.number.sends_the_number()
        self.NumberTwoDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 7, "result is not as expected"

        self.validate_vdevice_references()

    def validate_vdevice_references(self):
        assert self.Calculator.adds.get_number_of_provider_1() == self.NumberOneDevice.number.get_number(), \
            f"the currently mapped internal vdevice returns an unexpected value " \
            f"`{self.Calculator.adds.get_number_of_provider_1()}` " \
            f"(expected `{self.NumberOneDevice.number.get_number()}`)"

        try:
            self.Calculator.adds.get_number_of_provider_2()
            assert False, "provider 2 does return a value -> not allowed, because this VDevice was not mapped"
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

