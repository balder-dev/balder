from ...lib.features import FeatureV
from ...balderglob import RuntimeObserver


class SetupFeatureV(FeatureV):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureV, SetupFeatureV.do_something, "enter `SetupFeatureI.do_something`",
            category="feature")
