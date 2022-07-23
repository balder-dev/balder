import balder
from ..balderglob import RuntimeObserver


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")


class FeatureII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")


class FeatureOfRelevanceLvl1(balder.Feature):

    class VDeviceWithI(balder.VDevice):
        i = FeatureI()

    class VDeviceWithII(balder.VDevice):
        i = FeatureII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureOfRelevanceLvl1, FeatureOfRelevanceLvl1.do_something,
            "enter `FeatureOfRelevanceLvl1.do_something`", category="feature")


class FeatureOfRelevanceLvl2(FeatureOfRelevanceLvl1):
    """this feature will be used in scenario"""

    class VDeviceWithI(FeatureOfRelevanceLvl1.VDeviceWithI):
        i = FeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureOfRelevanceLvl2, FeatureOfRelevanceLvl2.do_something,
            "enter `FeatureOfRelevanceLvl2.do_something`", category="feature")
