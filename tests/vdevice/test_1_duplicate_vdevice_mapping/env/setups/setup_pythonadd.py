import balder
from ..lib.features import UnusedFeatureForUnusedVDevice
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate()

    class DoNothingDevice(balder.Device):
        unused = UnusedFeatureForUnusedVDevice()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
