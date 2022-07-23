import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature, UnusedFeatureForUnusedVDevice


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    class DoNothingDevice(balder.Device):
        unused = UnusedFeatureForUnusedVDevice()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(balder.Device):
        # this is not allowed -> should throw an error
        number = ProvidesANumberFeature(UselessDevice="DoNothingDevice", CalculatorDevice="Calculator")

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
