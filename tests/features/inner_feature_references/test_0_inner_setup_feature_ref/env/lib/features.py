import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.called_from_outer_feature, "enter `FeatureI.called_from_outer_feature`",
            category="feature")


class FeatureII(balder.Feature):
    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.called_from_outer_feature, "enter `FeatureII.called_from_outer_feature`",
            category="feature")


class FeatureIII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIII, FeatureIII.do_something, "enter `FeatureIII.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.called_from_outer_feature, "enter `FeatureIII.called_from_outer_feature`",
            category="feature")


class FeatureIV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.do_something, "enter `FeatureIV.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.called_from_outer_feature, "enter `FeatureIV.called_from_outer_feature`",
            category="feature")

