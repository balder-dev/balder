import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature
from .scenario_adding import ScenarioAdding


class ScenarioAddingChild(ScenarioAdding):

    # remove all connection -> test should check if we use the parent connections in case there are no connections
    class Calculator(ScenarioAdding.Calculator):
        adds = AddCalculateFeature()

    # only set the connection for `NumberOneDevice`
    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(ScenarioAdding.NumberOneDevice):
        number = ProvidesANumberFeature()

    class NumberTwoDevice(ScenarioAdding.NumberTwoDevice):
        number = ProvidesANumberFeature()

    def test_add_two_numbers(self):
        self.NumberOneDevice.number.set_number(3)
        self.NumberOneDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 3, "result is not as expected"
