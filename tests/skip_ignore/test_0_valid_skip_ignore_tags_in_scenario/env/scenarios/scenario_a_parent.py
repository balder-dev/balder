import balder
import logging
from ..lib.features import FeatureI, FeatureII
from ..lib.connections import AConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__file__)


class ScenarioAParent(balder.Scenario):
    """This is the scenario of category A"""
    IGNORE = ['test_a_1']
    SKIP = ['test_a_2']

    class ScenarioDevice1(balder.Device):
        i = FeatureI()

    @balder.connect(ScenarioDevice1, over_connection=AConnection)
    class ScenarioDevice2(balder.Device):
        ii = FeatureII()

    def test_a_1(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioAParent.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    def test_a_2(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.test_a_2, category="testcase",
                                  msg=f"execute Test `{ScenarioAParent.test_a_2.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    def test_a_3(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.test_a_3, category="testcase",
                                  msg=f"execute Test `{ScenarioAParent.test_a_3.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAParent, ScenarioAParent.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
