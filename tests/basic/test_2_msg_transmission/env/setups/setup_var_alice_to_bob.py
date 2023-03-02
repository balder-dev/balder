import balder
from .features_setup import SendOverLocalVarFeature, ReceiveOverLocalVarFeature


class SetupVarAliceToBob(balder.Setup):
    class Alice(balder.Device):
        send = SendOverLocalVarFeature()

    @balder.connect(with_device=Alice, over_connection=balder.Connection())
    class Bob(balder.Device):
        recv = ReceiveOverLocalVarFeature()
