from ...lib.features import FeatureII
from ...balderglob import RuntimeObserver


class SetupFeatureII2(FeatureII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII2, SetupFeatureII2.do_something, "enter `SetupFeatureIIB.do_something`",
            category="feature")

