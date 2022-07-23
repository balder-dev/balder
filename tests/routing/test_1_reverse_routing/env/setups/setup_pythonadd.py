import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()

    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

    @balder.connect(NumberProvider1, over_connection=MySimplySharedMemoryConnection)
    @balder.connect(NumberProvider2, over_connection=MySimplySharedMemoryConnection)
    class Calculator(balder.Device):
        calc = PyAddCalculate()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
