import balder
from ..lib.utils import SharedObj
from .features_setup import PyAddCalculate, PyAddProvideANumber
from .setup_pythonadd import SetupPythonAdd


class SetupPythonAddChild(SetupPythonAdd):

    class Calculator(SetupPythonAdd.Calculator):
        calc = PyAddCalculate()

    class NumberProvider1(SetupPythonAdd.NumberProvider1):
        n = PyAddProvideANumber()

    class NumberProvider2(SetupPythonAdd.NumberProvider2):
        n = PyAddProvideANumber()

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
