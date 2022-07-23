import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from .features_setup import IllegalFeature, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator(balder.Device):
        # this is the feature that will be overwritten in `SetupPythonAddChild` with a complete other feature
        calc = IllegalFeature()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()

    @balder.connect(Calculator, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
