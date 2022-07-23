import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()

    @balder.connect(Calculator, over_connection=balder.Connection)
    class NumberTwoDevice(balder.Device):
        number = ProvidesANumberFeature()
