from ...lib.features import NewlyDefinedFeature
from ...balderglob import RuntimeObserver


class NewlySetupFeature(NewlyDefinedFeature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, NewlySetupFeature, NewlySetupFeature.do_something, "enter `NewlySetupFeature.do_something`",
            category="feature")
