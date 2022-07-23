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
    def fixture_setup_session(self, balderglob_fixture_session):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert balderglob_fixture_session == FixtureReturn.BALDERGLOB_SESSION

        yield FixtureReturn.SETUP_SESSION

        assert isinstance(self, SetupA)
        assert balderglob_fixture_session == FixtureReturn.BALDERGLOB_SESSION
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup_setup(self, balderglob_fixture_setup, fixture_setup_session):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert balderglob_fixture_setup == FixtureReturn.BALDERGLOB_SETUP
        assert fixture_setup_session == FixtureReturn.SETUP_SESSION

        yield FixtureReturn.SETUP_SETUP

        assert isinstance(self, SetupA)
        assert balderglob_fixture_setup == FixtureReturn.BALDERGLOB_SETUP
        assert fixture_setup_session == FixtureReturn.SETUP_SESSION
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_setup_scenario(self, balderglob_fixture_scenario, fixture_setup_setup):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert balderglob_fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO
        assert fixture_setup_setup == FixtureReturn.SETUP_SETUP

        yield FixtureReturn.SETUP_SCENARIO

        assert isinstance(self, SetupA)
        assert balderglob_fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO
        assert fixture_setup_setup == FixtureReturn.SETUP_SETUP
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_setup_variation(self, balderglob_fixture_variation, fixture_setup_scenario):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert balderglob_fixture_variation == FixtureReturn.BALDERGLOB_VARIATION
        assert fixture_setup_scenario == FixtureReturn.SETUP_SCENARIO

        yield FixtureReturn.SETUP_VARIATION

        assert isinstance(self, SetupA)
        assert balderglob_fixture_variation == FixtureReturn.BALDERGLOB_VARIATION
        assert fixture_setup_scenario == FixtureReturn.SETUP_SCENARIO
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_setup_testcase(self, balderglob_fixture_testcase, fixture_setup_variation):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        assert isinstance(self, SetupA)
        assert balderglob_fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE
        assert fixture_setup_variation == FixtureReturn.SETUP_VARIATION

        yield FixtureReturn.SETUP_TESTCASE

        assert isinstance(self, SetupA)
        assert balderglob_fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE
        assert fixture_setup_variation == FixtureReturn.SETUP_VARIATION
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
