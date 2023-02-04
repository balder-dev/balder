import balder


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
    """
    note: Although this feature has two vdevices that define a number provider, please note that multiple vdevice
    mappings are not yet supported.
    """

    all_numbers = []

    class ANumberProviderDevice1(balder.VDevice):
        provider = ProvidesANumberFeature()

    class ANumberProviderDevice2(balder.VDevice):
        provider = ProvidesANumberFeature()

    def get_numbers(self):
        """this method get all the single numbers that should be calculated"""
        raise NotImplementedError("has to be implemented in subclass")

    def add_numbers(self):
        """this method adds all the numbers"""
        raise NotImplementedError("has to be implemented in subclass")

    def get_number_of_provider_1(self):
        return self.ANumberProviderDevice1.provider.get_number()

    def get_number_of_provider_2(self):
        return self.ANumberProviderDevice2.provider.get_number()
