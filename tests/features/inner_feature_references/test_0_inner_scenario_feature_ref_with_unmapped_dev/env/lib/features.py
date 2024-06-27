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
    feature_i = FeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")
        self.feature_i.called_from_outer_feature()

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
            __file__, FeatureIV, FeatureIV.called_from_outer_feature,
            "enter `FeatureIII.called_from_outer_feature`", category="feature")


class FeatureIV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.do_something, "enter `FeatureIV.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureIV, FeatureIV.called_from_outer_feature,
            "enter `FeatureIV.called_from_outer_feature`", category="feature")


class FeatureV(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureV, FeatureV.do_something, "enter `FeatureV.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureV, FeatureV.called_from_outer_feature, "enter `FeatureV.called_from_outer_feature`",
            category="feature")


class FeatureVI(balder.Feature):
    feature_v = FeatureV()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVI, FeatureVI.do_something, "enter `FeatureVI.do_something`", category="feature")
        self.feature_v.called_from_outer_feature()

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVI, FeatureVI.called_from_outer_feature,
            "enter `FeatureVI.called_from_outer_feature`", category="feature")


class FeatureVII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVII, FeatureVII.do_something, "enter `FeatureVII.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVII, FeatureVII.called_from_outer_feature,
            "enter `FeatureVII.called_from_outer_feature`", category="feature")


class FeatureVIII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVIII, FeatureVIII.do_something,
            "enter `FeatureVIII.do_something`", category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVIII, FeatureVIII.called_from_outer_feature,
            "enter `FeatureVIII.called_from_outer_feature`", category="feature")

