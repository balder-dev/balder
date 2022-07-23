import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()

    class NumberTwoDevice(balder.Device):
        number = ProvidesANumberFeature()

    def test_add_two_numbers(self):
        self.NumberOneDevice.number.set_number(3)
        self.NumberOneDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 3, "result is not as expected"
