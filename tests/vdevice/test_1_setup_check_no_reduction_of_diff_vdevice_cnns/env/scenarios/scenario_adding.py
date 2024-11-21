import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature, VDeviceHelperFeature1, VDeviceHelperFeature2, \
    VDeviceHelperFeature3
from ..lib.connections import SimulatedParentConnection, SimulatedChildConnection, MySimplySharedMemoryConnection


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    @balder.connect(Calculator, over_connection=balder.Connection.based_on(
        (SimulatedChildConnection.based_on(SimulatedParentConnection) & MySimplySharedMemoryConnection)))
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()
        special_1 = VDeviceHelperFeature1()
        special_2 = VDeviceHelperFeature2()
        special_3 = VDeviceHelperFeature3()

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
