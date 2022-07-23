import balder
from ...lib.features import FeatureII
from ...lib.connections import ChildBConnection
from ...balderglob import RuntimeObserver


# this forces that the mapped vDevice has to have a `ChildBConnection` - all other of the conn-tree has to be removed
# for further processing
@balder.for_vdevice("VDeviceFeatureI", ChildBConnection)
class SetupFeatureII(FeatureII):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")
