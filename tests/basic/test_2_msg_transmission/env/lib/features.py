from typing import Union
import balder


class ReceiveMessageFeature(balder.Feature):

    def start_listening(self) -> None:
        raise NotImplementedError("this method has to be implemented on setup level")

    def get_next_received_msg(self) -> Union[str, None]:
        raise NotImplementedError("this method has to be implemented on setup level")


class SendMessageFeature(balder.Feature):
    class Receiver(balder.VDevice):
        recv = ReceiveMessageFeature()

    def send(self, message: str) -> None:
        raise NotImplementedError("this method has to be implemented on setup level")
