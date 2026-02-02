from ...lib.features import FeatureIII
from ...balderglob import RuntimeObserver


class SetupFeatureIII(FeatureIII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureIII, SetupFeatureIII.do_something, "enter `SetupFeatureIII.do_something`",
            category="feature")
