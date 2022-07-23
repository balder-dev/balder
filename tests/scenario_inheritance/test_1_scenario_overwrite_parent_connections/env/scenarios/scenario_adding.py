import balder
import balder.connections as cnns
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature


class ScenarioAdding(balder.Scenario):

    class Calculator(balder.Device):
        # we could add vDevices here later too -> f.e. `NumberOne="NumberOneDevice", NumberTwo="NumberTwoDevice"`
        adds = AddCalculateFeature()

    # only set the connection for `NumberTwoDevice`
    class NumberOneDevice(balder.Device):
        number = ProvidesANumberFeature()

    @balder.connect(Calculator, over_connection=cnns.HttpConnection)
    class NumberTwoDevice(balder.Device):
        number = ProvidesANumberFeature()
