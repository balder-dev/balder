import balder
from ..balderglob import RuntimeObserver
from ..lib.connections import ChildAConnection, ChildBConnection


class FeatureI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something, "enter `FeatureI.do_something`", category="feature")

    def do_something_special(self):
        RuntimeObserver.add_entry(
            __file__, FeatureI, FeatureI.do_something_special, "enter `FeatureI.do_something_special`",
            category="feature")


# this allows `ChildAConnection` AND `ChildBConnection` connections (both setups could work on scenario level - setup
# level limits this)
@balder.for_vdevice("VDeviceFeatureI", with_connections=balder.Connection.based_on(ChildAConnection | ChildBConnection))
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
