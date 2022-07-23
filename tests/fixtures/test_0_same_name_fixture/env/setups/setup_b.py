import balder
import logging
from .setup_features import SetupFeatureIII, SetupFeatureIV
from ..lib.connections import BConnection
from ..lib.utils import FixtureReturn
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupB(balder.Setup):
    """This is a setup of category B (exactly the same as scenario B)"""

    class SetupDevice3(balder.Device):
        s_iii = SetupFeatureIII()

    @balder.connect(SetupDevice3, over_connection=BConnection)
    class SetupDevice4(balder.Device):
        s_iv = SetupFeatureIV()

    @balder.fixture(level="session")
    def fixture_session(self, fixture_session):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_session,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        assert isinstance(self, SetupB)
        assert fixture_session == FixtureReturn.BALDERGLOB_SESSION

        yield FixtureReturn.SETUP_B_SESSION

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_session,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self, fixture_session, fixture_setup):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_setup,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        assert isinstance(self, SetupB)
        assert fixture_session == FixtureReturn.SETUP_B_SESSION
        assert fixture_setup == FixtureReturn.BALDERGLOB_SETUP

        yield FixtureReturn.SETUP_B_SETUP

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_setup,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self, fixture_session, fixture_setup, fixture_scenario):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_scenario,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        assert isinstance(self, SetupB)
        assert fixture_session == FixtureReturn.SETUP_B_SESSION
        assert fixture_setup == FixtureReturn.SETUP_B_SETUP
        assert fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO

        yield FixtureReturn.SETUP_B_SCENARIO

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_scenario,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_variation,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        assert isinstance(self, SetupB)
        assert fixture_session == FixtureReturn.SETUP_B_SESSION
        assert fixture_setup == FixtureReturn.SETUP_B_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_B_SCENARIO
        assert fixture_variation == FixtureReturn.BALDERGLOB_VARIATION

        yield FixtureReturn.SETUP_B_VARIATION

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_variation,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_testcase,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        assert isinstance(self, SetupB)
        assert fixture_session == FixtureReturn.SETUP_B_SESSION
        assert fixture_setup == FixtureReturn.SETUP_B_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_B_SCENARIO
        assert fixture_variation == FixtureReturn.SETUP_B_VARIATION
        assert fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE

        yield FixtureReturn.SETUP_B_TESTCASE

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_testcase,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()
