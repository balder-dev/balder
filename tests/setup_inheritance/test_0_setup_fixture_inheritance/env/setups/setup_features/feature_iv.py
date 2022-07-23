from ...lib.features import FeatureIV
from ...balderglob import RuntimeObserver


class SetupFeatureIV(FeatureIV):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIV, SetupFeatureIV.do_something, "enter `SetupFeatureIV.do_something`",
            category="feature")
