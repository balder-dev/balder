import balder
from ...lib.features import ScenarioMethVarFeature
from ...balderglob import RuntimeObserver


@balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
class BetweenMethVarFeature(ScenarioMethVarFeature):
    """This is the feature class that is between the scenario class and the setup class."""
    class VDeviceI(ScenarioMethVarFeature.VDeviceI):
        pass

    class VDeviceII(ScenarioMethVarFeature.VDeviceII):
        pass

    class VDeviceIII(ScenarioMethVarFeature.VDeviceIII):
        pass

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, BetweenMethVarFeature, BetweenMethVarFeature.do_something,
            "enter `BetweenMethVarFeature.do_something`",
            category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, BetweenMethVarFeature, BetweenMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI><BetweenMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, BetweenMethVarFeature, BetweenMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceII><BetweenMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, BetweenMethVarFeature, BetweenMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceIII><BetweenMethVarFeature.do_something_as_var>", category="feature")

