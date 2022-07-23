from ...lib.features import FeatureII
from ...balderglob import RuntimeObserver


class SetupFeatureII(FeatureII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")

