import balder
from ..lib.features import SendMessageFeature, ReceiveMessageFeature


class ScenarioSenderAndReceiver(balder.Scenario):
    class SenderDevice(balder.Device):
        send = SendMessageFeature(Receiver="ReceiverDevice")

    @balder.connect(with_device=SenderDevice, over_connection=balder.Connection())
    class ReceiverDevice(balder.Device):
        recv = ReceiveMessageFeature()

    def test_send_a_message(self):
        msg_content = "my nice message"

        self.ReceiverDevice.recv.start_listening()
        self.SenderDevice.send.send(msg_content)

        assert self.ReceiverDevice.recv.get_next_received_msg() == msg_content, \
            "receiver does not receive the sent message "
