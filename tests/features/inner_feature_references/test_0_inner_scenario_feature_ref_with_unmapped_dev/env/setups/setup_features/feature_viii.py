from ...lib.features import FeatureVII, FeatureVIII
from ...balderglob import RuntimeObserver


class SetupFeatureVIII(FeatureVIII):
    feature_vii = FeatureVII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVIII, SetupFeatureVIII.do_something, "enter `SetupFeatureVIII.do_something`",
            category="feature")
        self.feature_vii.called_from_outer_feature()

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVIII, SetupFeatureVIII.called_from_outer_feature,
            "enter `SetupFeatureVIII.called_from_outer_feature`", category="feature")
