import balder
import logging
from ..lib.features import FeatureI, FeatureII
from ..lib.connections import AConnection
from ..balderglob import RuntimeObserver
from .scenario_a import ScenarioA

logger = logging.getLogger(__file__)


class ScenarioAChild(ScenarioA):
    """This is the CHILD scenario of category A"""

    class ScenarioDevice1(ScenarioA.ScenarioDevice1):
        i = FeatureI()

    @balder.connect(ScenarioDevice1, over_connection=AConnection)
    class ScenarioDevice2(ScenarioA.ScenarioDevice2):
        ii = FeatureII()

    def test_a_1(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild, ScenarioAChild.test_a_1, category="testcase",
                                  msg=f"execute Test `{ScenarioAChild.test_a_1.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()

    def test_a_2(self):
        RuntimeObserver.add_entry(__file__, ScenarioAChild, ScenarioAChild.test_a_2, category="testcase",
                                  msg=f"execute Test `{ScenarioAChild.test_a_2.__qualname__}`")
        self.ScenarioDevice1.i.do_something()
        self.ScenarioDevice2.ii.do_something()
