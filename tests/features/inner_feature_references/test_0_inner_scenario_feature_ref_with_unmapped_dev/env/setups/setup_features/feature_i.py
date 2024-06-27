from ...lib.features import FeatureI
from ...balderglob import RuntimeObserver


class SetupFeatureI(FeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureI, SetupFeatureI.do_something, "enter `SetupFeatureI.do_something`",
            category="feature")

    def called_from_outer_feature(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureI, SetupFeatureI.called_from_outer_feature,
            "enter `SetupFeatureI.called_from_outer_feature`", category="feature")
