import balder
import logging
from ..lib.features import FeatureVDeviceI, FeatureVDeviceII, FeatureVDeviceIII
from .setup_features import SetupMethVarFeature
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupIII(balder.Setup):
    """This is a setup that is used with `VDeviceIII` (matches with scenario A)"""

    class SetupDevice1(balder.Device):
        s_i = FeatureVDeviceI()
        s_ii = FeatureVDeviceII()
        s_iii = FeatureVDeviceIII()

    @balder.connect(SetupDevice1, over_connection=balder.Connection())
    class SetupDevice2(balder.Device):
        s_ii = SetupMethVarFeature(VDeviceIII="SetupDevice1")

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_session, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_scenario, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_variation, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

        yield

        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_testcase, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

        yield

        RuntimeObserver.add_entry(__file__, SetupIII, SetupIII.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()
