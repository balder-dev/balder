import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII
from ..lib.connections import AConnection
from ..lib.utils import FixtureReturn
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupA(balder.Setup):
    """This is a setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(balder.Device):
        s_i = SetupFeatureI()

    @balder.connect(SetupDevice1, over_connection=AConnection)
    class SetupDevice2(balder.Device):
        s_ii = SetupFeatureII()

    @balder.fixture(level="session")
    def fixture_session(self, fixture_session):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_session, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert fixture_session == FixtureReturn.BALDERGLOB_SESSION

        yield FixtureReturn.SETUP_A_SESSION

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self, fixture_session, fixture_setup):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert fixture_session == FixtureReturn.SETUP_A_SESSION
        assert fixture_setup == FixtureReturn.BALDERGLOB_SETUP

        yield FixtureReturn.SETUP_A_SETUP

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self, fixture_session, fixture_setup, fixture_scenario):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_scenario, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert fixture_session == FixtureReturn.SETUP_A_SESSION
        assert fixture_setup == FixtureReturn.SETUP_A_SETUP
        assert fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO

        yield FixtureReturn.SETUP_A_SCENARIO

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_variation, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert fixture_session == FixtureReturn.SETUP_A_SESSION
        assert fixture_setup == FixtureReturn.SETUP_A_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_A_SCENARIO
        assert fixture_variation == FixtureReturn.BALDERGLOB_VARIATION

        yield FixtureReturn.SETUP_A_VARIATION

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_testcase, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert fixture_session == FixtureReturn.SETUP_A_SESSION
        assert fixture_setup == FixtureReturn.SETUP_A_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_A_SCENARIO
        assert fixture_variation == FixtureReturn.SETUP_A_VARIATION
        assert fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE

        yield FixtureReturn.SETUP_A_TESTCASE

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
