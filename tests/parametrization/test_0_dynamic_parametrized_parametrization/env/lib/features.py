from typing import List
import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")

    def get_1(self):
        return 1


class FeatureII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")

    def get_dynamic_parameters(self, param1: int, param2: int) -> List[int]:
        raise NotImplementedError


class FeatureIII(balder.Feature):

    @property
    def params_from_property(self):
        return [1, 2, 3]

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIII, FeatureIII.do_something, "enter `FeatureIII.do_something`", category="feature")


class FeatureIV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.do_something, "enter `FeatureIV.do_something`", category="feature")

    def get_next_three_multiple_of(self, value: float) -> List[float]:
        return [value * 2, value * 3, value * 4]
