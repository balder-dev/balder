from ...lib.features import FeatureVI
from .feature_v import SetupFeatureV
from ...balderglob import RuntimeObserver


class SetupFeatureVI(FeatureVI):
    feature_v = SetupFeatureV()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVI, SetupFeatureVI.do_something, "enter `SetupFeatureVI.do_something`",
            category="feature")
        self.feature_v.called_from_outer_feature()

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVI, SetupFeatureVI.called_from_outer_feature,
            "enter `SetupFeatureVI.called_from_outer_feature`", category="feature")
