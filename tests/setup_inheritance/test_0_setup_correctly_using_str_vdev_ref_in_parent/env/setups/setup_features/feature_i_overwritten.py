from ...balderglob import RuntimeObserver
from .feature_i import SetupFeatureI


class SetupFeatureIOverwritten(SetupFeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIOverwritten, SetupFeatureIOverwritten.do_something,
            "enter `SetupFeatureIOverwritten.do_something`", category="feature")

    def call_over_vdev(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIOverwritten, SetupFeatureIOverwritten.call_over_vdev, "enter `SetupFeatureIOverwritten.call_over_vdev`", category="feature")
