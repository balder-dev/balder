import balder
import logging
from .setup_features import SetupFeatureIII, SetupFeatureIV
from ..lib.connections import ChildConnection, ParentConnection

logger = logging.getLogger(__name__)


class SetupB(balder.Setup):
    """This is a setup of category B (exactly the same as scenario B)"""

    class SetupDevice3(balder.Device):
        iii = SetupFeatureIII()

    @balder.connect(SetupDevice3, over_connection=ChildConnection.based_on(ParentConnection))
    class SetupDevice4(balder.Device):
        iv = SetupFeatureIV()
