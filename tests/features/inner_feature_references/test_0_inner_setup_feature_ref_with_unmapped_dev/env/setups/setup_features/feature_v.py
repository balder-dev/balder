from ...lib.features import FeatureV
from ...balderglob import RuntimeObserver


class SetupFeatureV(FeatureV):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureV, SetupFeatureV.do_something, "enter `SetupFeatureV.do_something`",
            category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureV, SetupFeatureV.called_from_outer_feature,
            "enter `SetupFeatureV.called_from_outer_feature`", category="feature")
