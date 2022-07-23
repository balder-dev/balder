import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII
from ..lib.connections import BetweenConnection

logger = logging.getLogger(__name__)


class SetupA(balder.Setup):
    """This is a setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(balder.Device):
        i = SetupFeatureI()

    @balder.connect(SetupDevice1, over_connection=BetweenConnection)
    class SetupDevice2(balder.Device):
        ii = SetupFeatureII()
