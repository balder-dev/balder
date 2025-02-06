import balder
from ...balderglob import RuntimeObserver


class SetupFeatureNew(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureNew, SetupFeatureNew.do_something, "enter `SetupFeatureNew.do_something`",
            category="feature")
