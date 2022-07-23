import balder
import logging
from ..lib.features import FeatureIII, FeatureIV
from ..lib.connections import BConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class ScenarioB(balder.Scenario):
    """This is the PARENT scenario of category B"""

    class ScenarioDevice3(balder.Device):
        iii = FeatureIII()

    @balder.connect(ScenarioDevice3, over_connection=BConnection)
    class ScenarioDevice4(balder.Device):
        iv = FeatureIV()

    def test_b_1(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.test_b_1, category="testcase",
                                  msg=f"execute Test `{ScenarioB.test_b_1.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    def test_b_2(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.test_b_2, category="testcase",
                                  msg=f"execute Test `{ScenarioB.test_b_2.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioB, ScenarioB.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()
