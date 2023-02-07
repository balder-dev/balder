import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator1(balder.Device):
        calc = PyAddCalculate()

    class Calculator2(balder.Device):
        calc = PyAddCalculate()

    @balder.connect(Calculator1, over_connection=MySimplySharedMemoryConnection)
    @balder.connect(Calculator2, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber(Calculator="Calculator1")

    @balder.connect(Calculator1, over_connection=MySimplySharedMemoryConnection)
    @balder.connect(Calculator2, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber(Calculator="Calculator1")

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
