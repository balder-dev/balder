import balder
from .features_setup import SendOverQueueFeature, ReceiveOverQueueFeature


class SetupQueueAliceToBob(balder.Setup):
    class Alice(balder.Device):
        send = SendOverQueueFeature()

    @balder.connect(with_device=Alice, over_connection=balder.Connection())
    class Bob(balder.Device):
        recv = ReceiveOverQueueFeature()
