import balder
from ..balderglob import RuntimeObserver


class FeatureVDeviceI(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVDeviceI, FeatureVDeviceI.do_something, "enter `FeatureVDeviceI.do_something`",
            category="feature")


class FeatureVDeviceII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVDeviceII, FeatureVDeviceII.do_something, "enter `FeatureVDeviceII.do_something`",
            category="feature")


class FeatureVDeviceIII(balder.Feature):

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, FeatureVDeviceIII, FeatureVDeviceIII.do_something, "enter `FeatureVDeviceIII.do_something`",
            category="feature")


@balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
class BaseMethVarFeature(balder.Feature):

    class VDeviceI(balder.VDevice):
        feat = FeatureVDeviceI()

    class VDeviceII(balder.VDevice):
        feat = FeatureVDeviceII()

    class VDeviceIII(balder.VDevice):
        feat = FeatureVDeviceIII()

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, BaseMethVarFeature, BaseMethVarFeature.do_something, "enter `BaseMethVarFeature.do_something`",
            category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
    def do_something_as_var(self):
        RuntimeObserver.add_entry(
            __file__, BaseMethVarFeature, BaseMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI><BaseMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
    def do_something_as_var(self):
        RuntimeObserver.add_entry(
            __file__, BaseMethVarFeature, BaseMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceII><BaseMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
    def do_something_as_var(self):
        RuntimeObserver.add_entry(
            __file__, BaseMethVarFeature, BaseMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceIII><BaseMethVarFeature.do_something_as_var>", category="feature")


@balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
@balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
class ScenarioMethVarFeature(BaseMethVarFeature):
    """This is our direct Scenario feature."""
    class VDeviceI(BaseMethVarFeature.VDeviceI):
        pass

    class VDeviceII(BaseMethVarFeature.VDeviceII):
        pass

    class VDeviceIII(BaseMethVarFeature.VDeviceIII):
        pass

    def do_something(self):
        RuntimeObserver.add_entry(
            __file__, ScenarioMethVarFeature, ScenarioMethVarFeature.do_something,
            "enter `ScenarioMethVarFeature.do_something`",
            category="feature")

    @balder.for_vdevice("VDeviceI", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, ScenarioMethVarFeature, ScenarioMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceI><ScenarioMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceII", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, ScenarioMethVarFeature, ScenarioMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceII><ScenarioMethVarFeature.do_something_as_var>", category="feature")

    @balder.for_vdevice("VDeviceIII", with_connections=balder.Connection())
    def do_something_as_var(self):
        super().do_something_as_var()
        RuntimeObserver.add_entry(
            __file__, ScenarioMethVarFeature, ScenarioMethVarFeature.do_something_as_var,
            "MethodVariation<VDeviceIII><ScenarioMethVarFeature.do_something_as_var>", category="feature")
