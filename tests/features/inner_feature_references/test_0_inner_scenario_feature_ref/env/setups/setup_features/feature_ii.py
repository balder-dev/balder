from ...lib.features import FeatureII
from ...balderglob import RuntimeObserver


class SetupFeatureII(FeatureII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")
        self.feature_i.called_from_outer_feature()

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.called_from_outer_feature,
            "enter `SetupFeatureII.called_from_outer_feature`", category="feature")
