from ...lib.features import FeatureI
from ...balderglob import RuntimeObserver


class SetupFeatureI(FeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureI, SetupFeatureI.do_something, "enter `SetupFeatureI.do_something`",
            category="feature")

    def call_over_vdev(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureI, SetupFeatureI.call_over_vdev, "enter `SetupFeatureI.call_over_vdev`", category="feature")

