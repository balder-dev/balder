import balder
from balder.parametrization import Parameter
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature, RandomNumberFeature


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()
        example = RandomNumberFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberTwoDevice(balder.Device):
        number = ProvidesANumberFeature()
        example = RandomNumberFeature()

    @balder.parametrize_by_feature('number1', (NumberOneDevice, 'example', 'get_random_numbers_higher_than'), parameter={'value': Parameter('number2')})
    @balder.parametrize_by_feature('number2', (NumberTwoDevice, 'example', 'get_random_numbers_higher_than'), parameter={'value': Parameter('number1')})
    def test_add_two_numbers(self, number1, number2):
        self.NumberOneDevice.number.set_number(number1)
        self.NumberTwoDevice.number.set_number(number2)

        self.NumberOneDevice.number.sends_the_number()
        self.NumberTwoDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 7, "result is not as expected"
