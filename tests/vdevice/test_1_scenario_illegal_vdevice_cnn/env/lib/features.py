import balder
import balder.connections as cnns


class AddCalculateFeature(balder.Feature):

    all_numbers = []

    def get_numbers(self):
        """this method get all the single numbers that should be calculated"""
        raise NotImplementedError("has to be implemented in subclass")

    def add_numbers(self):
        """this method adds all the numbers"""
        raise NotImplementedError("has to be implemented in subclass")


# the following connection binding is not used in the scenario
@balder.for_vdevice('CalculatorDevice', cnns.HttpConnection)
class ProvidesANumberFeature(balder.Feature):
    the_number = 0

    class CalculatorDevice(balder.VDevice):
        add = AddCalculateFeature()

    def set_number(self, number):
        """user method that allows to set the number"""
        self.the_number = number

    def get_number(self):
        """returns the set number"""
        raise NotImplementedError("has to be implemented in subclass")

    def sends_the_number(self):
        """sends the set number"""
        raise NotImplementedError("has to be implemented in subclass")
