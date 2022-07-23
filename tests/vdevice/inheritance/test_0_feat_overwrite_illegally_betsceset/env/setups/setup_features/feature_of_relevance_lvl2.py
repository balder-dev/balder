from ...lib.features import FeatureOfRelevanceLvl1, FeatureI, FeatureII, IllegalFeature
from ...balderglob import RuntimeObserver


class FeatureOfRelevanceLvl2(FeatureOfRelevanceLvl1):
    """this feature will be used nowhere"""

    class VDeviceWithI(FeatureOfRelevanceLvl1.VDeviceWithI):
        # overwrites the `FeatureI`, which is illegal because there is no relation between `IllegalFeature` and
        # `FeatureI`
        i = IllegalFeature()
        # we define this separately (to still support the requirement for a matching)
        another_one = FeatureI()

    class VDeviceWithII(FeatureOfRelevanceLvl1.VDeviceWithII):
        i = FeatureII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureOfRelevanceLvl2, FeatureOfRelevanceLvl2.do_something,
            "enter `FeatureOfRelevanceLvl2.do_something`", category="feature")
