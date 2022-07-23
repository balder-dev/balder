import balder
from ..lib.features import AddCalculateFeature, ProvidesANumberFeature
from ..lib.utils import SharedObj


class PyAddProvideANumber(ProvidesANumberFeature):

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


class IllegalFeature(balder.Feature):
    def get_numbers(self):
        self.all_numbers = SharedObj.shared_mem_list

    def add_numbers(self):
        result = 0
        for cur_number in self.all_numbers:
            result += cur_number
        return result