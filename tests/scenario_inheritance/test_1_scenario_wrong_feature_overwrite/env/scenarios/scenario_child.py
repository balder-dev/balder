import balder

from ..lib.features import AddCalculateFeature, ProvidesANumberFeature
from .scenario_adding import ScenarioAdding


class ScenarioChild(ScenarioAdding):

    class Calculator(ScenarioAdding.Calculator):
        # overwrites the feature `adds = IllegalFeature()` defined in `ScenarioAdding`
        adds = AddCalculateFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(ScenarioAdding.NumberOneDevice):
        number = ProvidesANumberFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberTwoDevice(ScenarioAdding.NumberTwoDevice):
        number = ProvidesANumberFeature()

    def test_add_two_numbers(self):
        self.NumberOneDevice.number.set_number(3)
        self.NumberTwoDevice.number.set_number(4)

        self.NumberOneDevice.number.sends_the_number()
        self.NumberTwoDevice.number.sends_the_number()

        self.Calculator.adds.get_numbers()
        result = self.Calculator.adds.add_numbers()
        assert result == 7, "result is not as expected"
