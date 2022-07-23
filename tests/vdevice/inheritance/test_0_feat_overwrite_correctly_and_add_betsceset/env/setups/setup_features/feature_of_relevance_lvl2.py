from ...lib.features import FeatureOfRelevanceLvl1, FeatureIChild, FeatureNewI, FeatureII
from ...balderglob import RuntimeObserver


class FeatureOfRelevanceLvl2(FeatureOfRelevanceLvl1):
    """this feature will be used nowhere"""

    class VDeviceWithI(FeatureOfRelevanceLvl1.VDeviceWithI):
        # overwrites the old one
        i = FeatureIChild()
        # defines a new one
        new = FeatureNewI()

    class VDeviceWithII(FeatureOfRelevanceLvl1.VDeviceWithII):
        i = FeatureII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureOfRelevanceLvl2, FeatureOfRelevanceLvl2.do_something,
            "enter `FeatureOfRelevanceLvl2.do_something`", category="feature")
