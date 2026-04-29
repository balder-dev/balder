import balder
from ...lib.features import FeatureI, FeatureII
from ...balderglob import RuntimeObserver


class SetupFeatureII(FeatureII):

    class Feat1VDev(balder.VDevice):
        feat1 = FeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")
        self.Feat1VDev.feat1.call_over_vdev()
