import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAddNoMapping(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProviderOne(balder.Device):
        n = PyAddProvideANumber()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProviderTwo(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
