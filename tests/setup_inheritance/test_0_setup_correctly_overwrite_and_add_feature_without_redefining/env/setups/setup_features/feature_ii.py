import balder
from ...lib.features import FeatureI, FeatureII
from ...balderglob import RuntimeObserver


class SetupFeatureII(FeatureII):

    class Dev1(balder.VDevice):
        feat = FeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")
