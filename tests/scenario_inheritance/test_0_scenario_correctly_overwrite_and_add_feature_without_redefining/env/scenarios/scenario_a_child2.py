import balder
import logging
from ..lib.features import FeatureIOverwritten, FeatureII, NewlyDefinedFeature
from ..lib.connections import AConnection
from ..balderglob import RuntimeObserver
from .scenario_a_parent import ScenarioAParent

logger = logging.getLogger(__file__)


class ScenarioAChild2(ScenarioAParent):
    """This is the CHILD scenario of category A"""

    class ScenarioDevice1(ScenarioAParent.ScenarioDevice1):
        i = FeatureIOverwritten()

    @balder.connect(ScenarioDevice1, over_connection=AConnection)
    class ScenarioDevice2(ScenarioAParent.ScenarioDevice2):
        new = NewlyDefinedFeature()

    def test_a_1(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioAChild2.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    def test_a_2(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.test_a_2, category="testcase",
                                  msg=f"execute Test `{ScenarioAChild2.test_a_2.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_setup, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioAChild2, ScenarioAChild2.fixture_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
        self.ScenarioDevice2.new.do_something()
