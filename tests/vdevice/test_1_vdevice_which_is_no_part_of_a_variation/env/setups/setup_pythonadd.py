import balder
from ..lib.connections import MySimplySharedMemoryConnection
from ..lib.utils import SharedObj
from ..lib.features import CalculatorHelperFeature
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class HelperDevice(balder.Device):
        """this device is no part of the variation, but used as vdevice"""
        helper = CalculatorHelperFeature()

    @balder.connect(HelperDevice, over_connection=balder.Connection)
    class Calculator1(balder.Device):
        calc = PyAddCalculate(Helper='HelperDevice')

    @balder.connect(Calculator1, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber(Calculator="Calculator1")

    @balder.connect(Calculator1, over_connection=MySimplySharedMemoryConnection)
    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber(Calculator="Calculator1")

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
