from ...lib.features import FeatureOfRelevanceLvl2
from ...balderglob import RuntimeObserver


class SetupFeatureOfRelevanceLvl3(FeatureOfRelevanceLvl2):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureOfRelevanceLvl3, SetupFeatureOfRelevanceLvl3.do_something,
            "enter `SetupFeatureOfRelevanceLvl3.do_something`", category="feature")
