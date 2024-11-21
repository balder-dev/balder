import balder
import logging
from ..lib.features import FeatureVDeviceI, FeatureVDeviceII, FeatureVDeviceIII
from ..lib.connections import AConnection, BConnection, CConnection
from .setup_features import SetupMethVarFeature
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupIIIAOrB(balder.Setup):
    """This is a setup that uses VDeviceIII and only has a connection `AConnection OR B`"""

    class SetupDevice1(balder.Device):
        s_i = FeatureVDeviceI()
        s_ii = FeatureVDeviceII()
        s_iii = FeatureVDeviceIII()

    @balder.connect(SetupDevice1, over_connection=balder.Connection.based_on(AConnection | BConnection))
    class SetupDevice2(balder.Device):
        s_ii = SetupMethVarFeature(VDeviceIII="SetupDevice1")

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_setup, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

        yield

        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()

        yield

        RuntimeObserver.add_entry(__file__, SetupIIIAOrB, SetupIIIAOrB.fixture_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
        self.SetupDevice2.s_ii.do_something_as_var()
