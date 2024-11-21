import balder
from .between_meth_var_feature import BetweenMethVarFeature
from ...lib.connections import AConnection, BConnection, CConnection
from ...balderglob import RuntimeObserver


@balder.for_vdevice("VDeviceI", with_connections=balder.Connection.based_on(AConnection | BConnection | CConnection))
@balder.for_vdevice("VDeviceII", with_connections=balder.Connection.based_on(AConnection | BConnection))
@balder.for_vdevice("VDeviceIII", with_connections=balder.Connection.based_on(BConnection | (AConnection & BConnection)))
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

    @balder.for_vdevice("VDeviceI", with_connections=AConnection)
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI|AConnection><SetupMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=BConnection)
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI|BConnection><SetupMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=CConnection)
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI|CConnection><SetupMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceII", with_connections=balder.Connection.based_on(AConnection | BConnection))
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceII|AConnection+OR+BConnection><SetupMethVarFeature.do_something_as_var>",
            category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=BConnection)
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceIII|BConnection><SetupMethVarFeature.do_something_as_var>",
            category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=balder.Connection.based_on(AConnection & BConnection))
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, SetupMethVarFeature, SetupMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceIII|AConnection+AND+BConnection><SetupMethVarFeature.do_something_as_var>",
            category="feature")
