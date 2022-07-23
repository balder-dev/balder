import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII
from ..lib.connections import AConnection
from .setup_a import SetupA

logger = logging.getLogger(__name__)


class SetupAChild(SetupA):
    """This is the CHILD setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(SetupA.SetupDevice1):
        s_i = SetupFeatureI()

    @balder.connect(SetupDevice1, over_connection=AConnection)
    class SetupDevice2(SetupA.SetupDevice2):
        s_ii = SetupFeatureII()
