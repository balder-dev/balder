import balder
import logging
from ..lib.features import FeatureIII, FeatureIV
from ..lib.connections import BConnection
from ..lib.utils import FixtureReturn
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class ScenarioB(balder.Scenario):
    """This is the scenario of category B"""

    class ScenarioDevice3(balder.Device):
        iii = FeatureIII()

    @balder.connect(ScenarioDevice3, over_connection=BConnection)
    class ScenarioDevice4(balder.Device):
        iv = FeatureIV()

    def test_b_1(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.test_b_1, category="testcase",
                                  msg=f"execute Test `{ScenarioB.test_b_1.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_B_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_B_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_B_VARIATION
        assert fixture_testcase == FixtureReturn.SCENARIO_B_TESTCASE

    def test_b_2(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.test_b_2, category="testcase",
                                  msg=f"execute Test `{ScenarioB.test_b_2.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_B_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_B_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_B_VARIATION
        assert fixture_testcase == FixtureReturn.SCENARIO_B_TESTCASE

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)

        yield FixtureReturn.SCENARIO_B_SESSION

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self, fixture_session, fixture_setup):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SETUP_B_SETUP

        yield FixtureReturn.SCENARIO_B_SETUP

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self, fixture_session, fixture_setup, fixture_scenario):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_B_SETUP
        assert fixture_scenario == FixtureReturn.SETUP_B_SCENARIO

        yield FixtureReturn.SCENARIO_B_SCENARIO

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_B_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_B_SCENARIO
        assert fixture_variation == FixtureReturn.SETUP_B_VARIATION

        yield FixtureReturn.SCENARIO_B_VARIATION

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self, fixture_session, fixture_setup, fixture_scenario, fixture_variation, fixture_testcase):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        assert isinstance(self, ScenarioB)
        assert fixture_session == FixtureReturn.SCENARIO_B_SESSION
        assert fixture_setup == FixtureReturn.SCENARIO_B_SETUP
        assert fixture_scenario == FixtureReturn.SCENARIO_B_SCENARIO
        assert fixture_variation == FixtureReturn.SCENARIO_B_VARIATION
        assert fixture_testcase == FixtureReturn.SETUP_B_TESTCASE

        yield FixtureReturn.SCENARIO_B_TESTCASE

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()
