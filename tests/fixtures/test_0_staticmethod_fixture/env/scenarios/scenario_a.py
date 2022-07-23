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

    def test_a_1(self, fixture_scenario_session, fixture_scenario_setup, fixture_scenario_scenario,
                 fixture_scenario_variation, fixture_scenario_testcase, fixture_setup_session, fixture_setup_setup,
                 fixture_setup_scenario, fixture_setup_variation, fixture_setup_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioA.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert fixture_scenario_session == FixtureReturn.SCENARIO_SESSION
        assert fixture_scenario_setup == FixtureReturn.SCENARIO_SETUP
        assert fixture_scenario_scenario == FixtureReturn.SCENARIO_SCENARIO
        assert fixture_scenario_variation == FixtureReturn.SCENARIO_VARIATION
        assert fixture_scenario_testcase == FixtureReturn.SCENARIO_TESTCASE
        assert fixture_setup_session == FixtureReturn.SETUP_SESSION
        assert fixture_setup_setup == FixtureReturn.SETUP_SETUP
        assert fixture_setup_scenario == FixtureReturn.SETUP_SCENARIO
        assert fixture_setup_variation == FixtureReturn.SETUP_VARIATION
        assert fixture_setup_testcase == FixtureReturn.SETUP_TESTCASE

    @staticmethod
    @balder.fixture(level="session")
    def fixture_scenario_session(balderglob_fixture_session):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_session == FixtureReturn.BALDERGLOB_SESSION

        yield FixtureReturn.SCENARIO_SESSION

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_session == FixtureReturn.BALDERGLOB_SESSION

    @balder.fixture(level="setup")
    def fixture_scenario_setup(self, balderglob_fixture_setup, fixture_setup_setup, fixture_scenario_session):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert balderglob_fixture_setup == FixtureReturn.BALDERGLOB_SETUP
        assert fixture_scenario_session == FixtureReturn.SCENARIO_SESSION
        assert fixture_setup_setup == FixtureReturn.SETUP_SETUP

        yield FixtureReturn.SCENARIO_SETUP

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_setup, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert balderglob_fixture_setup == FixtureReturn.BALDERGLOB_SETUP
        assert fixture_scenario_session == FixtureReturn.SCENARIO_SESSION
        assert fixture_setup_setup == FixtureReturn.SETUP_SETUP

    @staticmethod
    @balder.fixture(level="scenario")
    def fixture_scenario_scenario(balderglob_fixture_scenario, fixture_setup_scenario, fixture_scenario_setup):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO
        assert fixture_scenario_setup == FixtureReturn.SCENARIO_SETUP
        assert fixture_setup_scenario == FixtureReturn.SETUP_SCENARIO

        yield FixtureReturn.SCENARIO_SCENARIO

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_scenario == FixtureReturn.BALDERGLOB_SCENARIO
        assert fixture_scenario_setup == FixtureReturn.SCENARIO_SETUP
        assert fixture_setup_scenario == FixtureReturn.SETUP_SCENARIO

    @balder.fixture(level="variation")
    def fixture_scenario_variation(self, balderglob_fixture_variation, fixture_setup_variation,
                                   fixture_scenario_scenario):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert balderglob_fixture_variation == FixtureReturn.BALDERGLOB_VARIATION
        assert fixture_scenario_scenario == FixtureReturn.SCENARIO_SCENARIO
        assert fixture_setup_variation == FixtureReturn.SETUP_VARIATION

        yield FixtureReturn.SCENARIO_VARIATION

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        assert isinstance(self, ScenarioA)
        assert balderglob_fixture_variation == FixtureReturn.BALDERGLOB_VARIATION
        assert fixture_scenario_scenario == FixtureReturn.SCENARIO_SCENARIO
        assert fixture_setup_variation == FixtureReturn.SETUP_VARIATION

    @staticmethod
    @balder.fixture(level="testcase")
    def fixture_scenario_testcase(balderglob_fixture_testcase, fixture_setup_testcase, fixture_scenario_variation):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE
        assert fixture_scenario_variation == FixtureReturn.SCENARIO_VARIATION
        assert fixture_setup_testcase == FixtureReturn.SETUP_TESTCASE

        yield FixtureReturn.SCENARIO_TESTCASE

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")
        ScenarioA.ScenarioDevice1.i.do_something()
        ScenarioA.ScenarioDevice2.ii.do_something()

        assert balderglob_fixture_testcase == FixtureReturn.BALDERGLOB_TESTCASE
        assert fixture_scenario_variation == FixtureReturn.SCENARIO_VARIATION
        assert fixture_setup_testcase == FixtureReturn.SETUP_TESTCASE
