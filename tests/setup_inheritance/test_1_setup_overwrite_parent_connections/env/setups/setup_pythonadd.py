import balder
import balder.connections as cnns
from .features_setup import PyAddCalculate, PyAddProvideANumber


class SetupPythonAdd(balder.Setup):

    class Calculator(balder.Device):
        calc = PyAddCalculate()

    @balder.connect(Calculator, over_connection=cnns.HttpConnection)
    class NumberProvider1(balder.Device):
        n = PyAddProvideANumber()

    class NumberProvider2(balder.Device):
        n = PyAddProvideANumber()

