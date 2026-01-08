from ...lib.features import FeatureI
from ...balderglob import RuntimeObserver


class SetupFeatureI2(FeatureI):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureI2, SetupFeatureI2.do_something, "enter `SetupFeatureIB.do_something`",
            category="feature")
