import balder


class UnusedFeatureForUnusedVDevice(balder.Feature):

    def do_nothing(self):
        pass


class AddCalculateFeature(balder.Feature):

    all_numbers = []

    def get_numbers(self):
        """this method get all the single numbers that should be calculated"""
        raise NotImplementedError("has to be implemented in subclass")

    def add_numbers(self):
        """this method adds all the numbers"""
        raise NotImplementedError("has to be implemented in subclass")


@balder.for_vdevice('UselessDevice', with_connections=balder.Connection)
@balder.for_vdevice('CalculatorDevice', with_connections=balder.Connection)
class ProvidesANumberFeature(balder.Feature):

    the_number = 0

    class UselessDevice(balder.VDevice):
        """a useless device that should help to validate this test"""
        nothing = UnusedFeatureForUnusedVDevice()

    class CalculatorDevice(balder.VDevice):
        """the other calculator device"""
        calc = AddCalculateFeature()

    def set_number(self, number):
        """user method that allows to set the number"""
        self.the_number = number

    def get_number(self):
        """returns the set number"""
        raise NotImplementedError("has to be implemented in subclass")

    def sends_the_number(self):
        """sends the set number"""
        raise NotImplementedError("has to be implemented in subclass")
