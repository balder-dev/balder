import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

        @classmethod
        def calculate_add(cls):
            # this should be validated -> on Scenario Level the used methods are not implemented
            # NOTE: Note that only class and static methods work here! We use no device instance and have no access
            cls.adds.get_numbers()
            return cls.adds.add_numbers()

        @staticmethod
        def static_calculate_add():
            # this should be validated -> on Scenario Level the used methods are not implemented
            # NOTE: Note that only class and static methods work here! We use no device instance and have no access
            ScenarioAdding.Calculator.adds.get_numbers()
            return ScenarioAdding.Calculator.adds.add_numbers()

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

        result = self.Calculator.calculate_add()
        assert result == 7, "result with class method is not as expected"

        result = self.Calculator.static_calculate_add()
        assert result == 7, "result with static method is not as expected"
