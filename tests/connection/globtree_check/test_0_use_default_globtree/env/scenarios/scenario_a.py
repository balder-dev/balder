import balder
import logging
from ..lib.features import FeatureI, FeatureII
from ..lib.connections import BetweenConnection

logger = logging.getLogger(__file__)


class ScenarioA(balder.Scenario):
    """This is the scenario of category A"""

    class ScenarioDevice1(balder.Device):
        i = FeatureI()

    @balder.connect(ScenarioDevice1, over_connection=BetweenConnection)
    class ScenarioDevice2(balder.Device):
        ii = FeatureII()

    def test_a_1(self):
        logger.info(f"execute testcase `{ScenarioA.test_a_1.__qualname__}`")
        assert True

    def test_a_2(self):
        logger.info(f"execute testcase `{ScenarioA.test_a_2.__qualname__}`")
        assert True
