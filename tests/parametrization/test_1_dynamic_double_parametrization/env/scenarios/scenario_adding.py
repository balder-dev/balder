import balder
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

    @balder.parametrize_by_feature('param', (NumberOneDevice, 'example', 'get_random_numbers'))
    @balder.parametrize_by_feature('param', (NumberTwoDevice, 'example', 'get_random_numbers'))
    def test_add_two_numbers(self, param):
        self.NumberOneDevice.number.set_number(3)
        self.NumberTwoDevice.number.set_number(4)

        self.NumberOneDevice.number.sends_the_number()
        self.NumberTwoDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 7, "result is not as expected"
