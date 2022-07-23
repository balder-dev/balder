import balder
from ..balderglob import RuntimeObserver
from ..lib.connections import ChildBConnection


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")

    def do_something_special(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something_special, "enter `FeatureI.do_something_special`",
            category="feature")


# this forces that the mapped vDevice has to have a `ChildBConnection` - all other of the conn-tree has to be removed
# for further processing
@balder.for_vdevice("VDeviceFeatureI", ChildBConnection)
class FeatureII(balder.Feature):

    class VDeviceFeatureI(balder.VDevice):
        vdevice_i = FeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something, "enter `FeatureII.do_something`", category="feature")

    def do_something_special_with_the_vdevice(self):
        RuntimeObserver.add_entry(
            __file__, FeatureII, FeatureII.do_something_special_with_the_vdevice,
            "enter `FeatureII.do_something_special_with_the_vdevice`", category="feature")
        self.VDeviceFeatureI.vdevice_i.do_something_special()
