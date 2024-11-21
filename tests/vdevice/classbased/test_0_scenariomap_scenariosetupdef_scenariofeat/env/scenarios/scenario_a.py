import balder
import logging
from ..lib.features import FeatureI, FeatureII
from ..lib.connections import ParentConnection, ChildBConnection, ChildAConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__file__)


class ScenarioA(balder.Scenario):
    """This is the scenario of category A"""

    class ScenarioDevice1(balder.Device):
        i = FeatureI()

    @balder.connect(ScenarioDevice1, over_connection=balder.Connection.based_on(
        ChildAConnection.based_on(ParentConnection) | ChildBConnection.based_on(ParentConnection)))
    class ScenarioDevice2(balder.Device):
        ii = FeatureII(VDeviceFeatureI="ScenarioDevice1")

    def test_a_1(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioA.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        self.ScenarioDevice2.ii.do_something_special_with_the_vdevice()

    def test_a_2(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.test_a_2, category="testcase",
                                  msg=f"execute Test `{ScenarioA.test_a_2.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        self.ScenarioDevice2.ii.do_something_special_with_the_vdevice()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, ScenarioA, ScenarioA.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
