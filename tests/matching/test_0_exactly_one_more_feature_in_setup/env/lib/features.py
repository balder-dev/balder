import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")


class FeatureII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")


class FeatureIII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIII, FeatureIII.do_something, "enter `FeatureIII.do_something`", category="feature")


class FeatureIV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.do_something, "enter `FeatureIV.do_something`", category="feature")


class FeatureV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureV, FeatureV.do_something, "enter `FeatureV.do_something`", category="feature")
