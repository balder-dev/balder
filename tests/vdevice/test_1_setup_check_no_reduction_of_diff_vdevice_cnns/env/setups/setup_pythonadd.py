import balder
from ..lib.features import VDeviceHelperFeature1, VDeviceHelperFeature2, VDeviceHelperFeature3
from ..lib.connections import MySimplySharedMemoryConnection, SimulatedParentConnection, SimulatedChildConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate()

    @balder.connect(Calculator, over_connection=balder.Connection.based_on(
        (SimulatedChildConnection.based_on(SimulatedParentConnection) & MySimplySharedMemoryConnection)))
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()
        special_1 = VDeviceHelperFeature1(CalculatorDevice="Calculator")
        special_2 = VDeviceHelperFeature2(CalculatorDevice="Calculator")
        special_3 = VDeviceHelperFeature3(CalculatorDevice="Calculator")

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
