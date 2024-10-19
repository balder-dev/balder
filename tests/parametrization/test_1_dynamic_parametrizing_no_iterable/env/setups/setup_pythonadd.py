import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from ..lib.features import RandomNumberFeature
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()
        example = RandomNumberFeature()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
