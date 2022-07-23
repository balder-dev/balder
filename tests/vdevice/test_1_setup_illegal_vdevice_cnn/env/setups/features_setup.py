import balder
import balder.connections as cnns
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature
from ..lib.utils import SharedObj


# the following connection binding is not used in the scenario
@balder.for_vdevice('CalculatorDevice', cnns.HttpConnection)
class PyAddProvideANumber(ProvidesANumberFeature):

    class CalculatorDevice(balder.VDevice):
        add = AddCalculateFeature()

    def get_number(self):
        return self.the_number

    def sends_the_number(self):
        SharedObj.shared_mem_list.append(self.the_number)


class PyAddCalculate(AddCalculateFeature):

    def get_numbers(self):
        self.all_numbers = SharedObj.shared_mem_list

    def add_numbers(self):
        result = 0
        for cur_number in self.all_numbers:
            result += cur_number
        return result
