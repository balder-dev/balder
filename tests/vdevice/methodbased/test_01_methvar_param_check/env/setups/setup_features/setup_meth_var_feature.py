import balder
from .between_meth_var_feature import BetweenMethVarFeature
from ...balderglob import RuntimeObserver


@balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
class SetupMethVarFeature(BetweenMethVarFeature):
    """This is the feature class that is directly being used in the setup."""
    class VDeviceI(BetweenMethVarFeature.VDeviceI):
        pass

    class VDeviceII(BetweenMethVarFeature.VDeviceII):
        pass

    class VDeviceIII(BetweenMethVarFeature.VDeviceIII):
        pass

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something,
            "enter `SetupMethVarFeature.do_something`",
            category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
    def do_something_as_var(self, a_int_val, a_str_val):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            f"MethodVariation<VDeviceI><SetupMethVarFeature.do_something_as_var> a_int_val={a_int_val} "
            f"a_str_val={a_str_val}", category="feature")

    @balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
    def do_something_as_var(self, a_int_val, a_str_val):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            f"MethodVariation<VDeviceII><SetupMethVarFeature.do_something_as_var> a_int_val={a_int_val} "
            f"a_str_val={a_str_val}", category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
    def do_something_as_var(self, a_int_val, a_str_val):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            f"MethodVariation<VDeviceIII><SetupMethVarFeature.do_something_as_var> a_int_val={a_int_val} "
            f"a_str_val={a_str_val}", category="feature")
