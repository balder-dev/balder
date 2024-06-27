from ...lib.features import FeatureVII
from ...balderglob import RuntimeObserver


class SetupFeatureVII(FeatureVII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVII, SetupFeatureVII.do_something, "enter `SetupFeatureVII.do_something`",
            category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureVII, SetupFeatureVII.called_from_outer_feature,
            "enter `SetupFeatureVII.called_from_outer_feature`", category="feature")
