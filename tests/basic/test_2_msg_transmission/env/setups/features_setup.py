from typing import Union
from queue import Queue
from ..lib.features import SendMessageFeature, ReceiveMessageFeature


class ReceiveOverLocalVarFeature(ReceiveMessageFeature):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.msg_buffer = []

    def start_listening(self) -> None:
        self.msg_buffer = []

    def get_next_received_msg(self) -> Union[str, None]:
        return self.msg_buffer.pop(0)


class SendOverLocalVarFeature(SendMessageFeature):

    class Receiver(SendMessageFeature.Receiver):
        recv = ReceiveOverLocalVarFeature()

    def send(self, message: str) -> None:
        self.Receiver.recv.msg_buffer.append(message)


class ReceiveOverQueueFeature(ReceiveMessageFeature):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue = Queue()

    def start_listening(self) -> None:
        self.queue = Queue()

    def get_next_received_msg(self) -> Union[str, None]:
        if self.queue.empty():
            return None
        return self.queue.get_nowait()


class SendOverQueueFeature(SendMessageFeature):
    class Receiver(SendMessageFeature.Receiver):
        recv = ReceiveOverQueueFeature()

    def send(self, message: str) -> None:
        self.Receiver.recv.queue.put(message)
