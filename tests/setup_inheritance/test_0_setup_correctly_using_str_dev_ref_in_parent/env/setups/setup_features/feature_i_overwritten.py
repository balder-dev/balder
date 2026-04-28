from ...balderglob import RuntimeObserver
from .feature_i import SetupFeatureI


class SetupFeatureIOverwritten(SetupFeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIOverwritten, SetupFeatureIOverwritten.do_something,
            "enter `SetupFeatureIOverwritten.do_something`", category="feature")
