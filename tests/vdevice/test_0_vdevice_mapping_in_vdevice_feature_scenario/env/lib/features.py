import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    class OtherVDevice2(balder.VDevice):
        pass

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")


class FeatureII(balder.Feature):

    class OtherVDevice1(balder.VDevice):
        # this mechanism is not allowed - normally you can not map a vDevice inside a vDevice feature -> should throw
        # an error while collecting
        my_feature_i = FeatureI(OtherVDevice2="OtherVDevice1")

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
