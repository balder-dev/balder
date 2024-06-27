from ...lib.features import FeatureIV
from ...balderglob import RuntimeObserver
from .feature_iii import SetupFeatureIII


class SetupFeatureIV(FeatureIV):
    feature_iii = SetupFeatureIII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIV, SetupFeatureIV.do_something, "enter `SetupFeatureIV.do_something`",
            category="feature")
        self.feature_iii.called_from_outer_feature()

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIV, SetupFeatureIV.called_from_outer_feature,
            "enter `SetupFeatureIV.called_from_outer_feature`", category="feature")
