import balder
from ...lib.features import FeatureII
from ...lib.connections import ChildBConnection
from ...balderglob import RuntimeObserver
from .feature_i import SetupFeatureI


# this forces that the mapped vDevice has to have a `ChildBConnection` - all other of the conn-tree has to be removed
# for further processing
@balder.for_vdevice("VDeviceFeatureI", ChildBConnection)
class SetupFeatureII(FeatureII):

    class VDeviceFeatureI(balder.VDevice):
        vdevice_i = SetupFeatureI()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")

    def do_something_special_with_the_vdevice(self):
        super(SetupFeatureII, self).do_something_special_with_the_vdevice()
        self.VDeviceFeatureI.vdevice_i.do_something_special()
