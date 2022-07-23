import balder
import logging
from ..lib.features import FeatureI, FeatureII
from ..lib.connections import AConnection
from ..lib.utils import FixtureReturn
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__file__)


class ScenarioA(balder.Scenario):
    """This is the scenario of category A"""

    class ScenarioDevice1(balder.Device):
        i = FeatureI()

    @balder.connect(ScenarioDevice1, over_connection=AConnection)
    class ScenarioDevice2(balder.Device):
        ii = FeatureII()

    def test_a_1(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioA.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_A_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_A_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_A_VARIATION
        assert fixture_testcase == FixtureReturn.SCENARIO_A_TESTCASE


    def test_a_2(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.test_a_2, category="testcase",
                                  msg=f"execute Test `{ScenarioA.test_a_2.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_A_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_A_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_A_VARIATION
        assert fixture_testcase == FixtureReturn.SCENARIO_A_TESTCASE

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)

        yield FixtureReturn.SCENARIO_A_SESSION

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self, fixture_session, fixture_setup):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SETUP_A_SETUP

        yield FixtureReturn.SCENARIO_A_SETUP

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self, fixture_session, fixture_setup, fixture_scenario):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_A_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_A_SCENARIO

        yield FixtureReturn.SCENARIO_A_SCENARIO

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_A_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_A_SCENARIO
        assert fixture_variation == FixtureReturn.SETUP_A_VARIATION

        yield FixtureReturn.SCENARIO_A_VARIATION

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_session == FixtureReturn.SCENARIO_A_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_A_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_A_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_A_VARIATION
        assert fixture_testcase == FixtureReturn.SETUP_A_TESTCASE

        yield FixtureReturn.SCENARIO_A_TESTCASE

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
