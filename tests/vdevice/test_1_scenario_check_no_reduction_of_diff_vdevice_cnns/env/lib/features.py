import balder
from .connections import SimulatedParentConnection, SimulatedChildConnection, MySimplySharedMemoryConnection


class ProvidesANumberFeature(balder.Feature):

    the_number = 0

    def set_number(self, number):
        """user method that allows to set the number"""
        self.the_number = number

    def get_number(self):
        """returns the set number"""
        raise NotImplementedError("has to be implemented in subclass")

    def sends_the_number(self):
        """sends the set number"""
        raise NotImplementedError("has to be implemented in subclass")


class AddCalculateFeature(balder.Feature):

    all_numbers = []

    def get_numbers(self):
        """this method get all the single numbers that should be calculated"""
        raise NotImplementedError("has to be implemented in subclass")

    def add_numbers(self):
        """this method adds all the numbers"""
        raise NotImplementedError("has to be implemented in subclass")


# the following connection is CONTAINED IN the scenario connection
@balder.for_vdevice('CalculatorDevice', SimulatedChildConnection.based_on(SimulatedParentConnection))
class VDeviceHelperFeature1(balder.Feature):
    """This is a helper feature that will be used to simulate this test."""
    class CalculatorDevice(balder.VDevice):
        add = AddCalculateFeature()


# the following connection is CONTAINED IN the scenario connection
@balder.for_vdevice('CalculatorDevice', SimulatedChildConnection)
class VDeviceHelperFeature2(balder.Feature):
    """This is a helper feature that will be used to simulate this test."""

    class CalculatorDevice(balder.VDevice):
        add = AddCalculateFeature()


# the following connection is CONTAINED IN the scenario connection
@balder.for_vdevice('CalculatorDevice', MySimplySharedMemoryConnection)
class VDeviceHelperFeature3(balder.Feature):
    """This is a helper feature that will be used to simulate this test."""

    class CalculatorDevice(balder.VDevice):
        add = AddCalculateFeature()
