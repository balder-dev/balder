import balder
import logging
from ..lib.features import FeatureIII, FeatureIV
from ..lib.connections import BetweenConnection

logger = logging.getLogger(__name__)


class ScenarioB(balder.Scenario):
    """This is the scenario of category B"""

    class ScenarioDevice3(balder.Device):
        iii = FeatureIII()

    @balder.connect(ScenarioDevice3, over_connection=BetweenConnection)
    class ScenarioDevice4(balder.Device):
        iv = FeatureIV()

    def test_b_1(self):
        logger.info(f"execute testcase `{ScenarioB.test_b_1.__qualname__}`")
        assert True

    def test_b_2(self):
        logger.info(f"execute testcase `{ScenarioB.test_b_2.__qualname__}`")
        assert True
