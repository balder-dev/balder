import balder
from ...lib.features import FeatureII
from ...balderglob import RuntimeObserver
from .feature_i import SetupFeatureI


class SetupFeatureII(FeatureII):

    class OtherVDevice1(balder.VDevice):
        # this mechanism is not allowed - normally you can not map a vDevice inside a vDevice feature -> should throw
        # an error while collecting
        my_feature_i = SetupFeatureI(OtherVDevice2="OtherVDevice1")

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupFeatureII, SetupFeatureII.do_something, "enter `SetupFeatureII.do_something`",
            category="feature")
