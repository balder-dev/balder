import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")


class FeatureIOverwritten(FeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIOverwritten, FeatureIOverwritten.do_something, "enter `FeatureIChild.do_something`",
            category="feature")


class FeatureII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")


class NewlyDefinedFeature(balder.Feature):
    """this feature will be instantiated in `ScenarioAChild` (and not in `ScenarioAParent`)"""
    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, NewlyDefinedFeature, NewlyDefinedFeature.do_something, "enter `NewlyDefinedFeature.do_something`",
            category="feature")


class FeatureIII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIII, FeatureIII.do_something, "enter `FeatureIII.do_something`", category="feature")


class FeatureIV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.do_something, "enter `FeatureIV.do_something`", category="feature")
