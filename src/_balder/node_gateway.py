from __future__ import annotations

from _balder.exceptions import NodeNotExistsError
from _balder.controllers import DeviceController


class NodeGateway:
    """
    This is a class that describes a gateway between two nodes of a device. A gateway enables the interaction of
    different connection nodes of a device.
    """

    def __init__(self, device, from_node: str, to_node: str, bidirectional: bool):
        """

        :param device: the device this gateway belongs to

        :param from_node: the node name where the gateway starts

        :param to_node: the node name where the gateway ends

        :param bidirectional: if this value is true, the gateway can "translate" in both directions
        """
        #: the device this gateway belongs to
        self.device = device

        #: the node name of the device the gateway starts
        self.from_node_name = from_node

        #: the node name of the device the gateway ends
        self.to_node_name = to_node

        #: if this value is true, the gateway can "translate" in both directions
        self._bidirectional = bidirectional

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def validate_given_node_names(self):
        """
        This method validates whether the given node names actually exist in the transferred device. Otherwise, this
        method throws an exception.
        """
        device_controller = DeviceController.get_for(self.device)
        if self.from_node_name not in device_controller.get_all_connections().keys():
            raise NodeNotExistsError(f"the from_node `{self.from_node_name}` mentioned by the `@gateway` decorator "
                                     f"does not exist as a node in device `{self.__class__.__name__}`")
        if self.to_node_name not in device_controller.get_all_connections().keys():
            raise NodeNotExistsError(f"the to_node `{self.to_node_name}` mentioned by the `@gateway` decorator does "
                                     f"not exist as a node in device `{self.__class__.__name__}`")

    def get_conn_partner_of(self, node) -> str:
        """
        This method returns the partner node of this gateway - it always returns the other not given side
        """
        if node not in (self.from_node_name, self.to_node_name):
            raise ValueError(f"the given node `{node}` is no component of this connection")

        return self.to_node_name if node == self.from_node_name else self.from_node_name

    def has_connection_from_to(self, start_node, end_node=None) -> bool:
        """
        This method checks if there is a connection from ``start_node`` to ``end_node``. This will always return true
        if the gateway supports bidirectional communication or the ``start_node`` and ``end_node`` given in this method
        are also the ``start_node`` and ``end_node`` mentioned in this connection object.

        .. note::
            Of course the given node names have to be the nodes mentioned internally!

        :param start_node: the node the connection should start

        :param end_node: the node the connection should end (optional, will be autofilled automatically)

        :return: returns true if the given direction is possible
        """
        if start_node not in (self.from_node_name, self.to_node_name):
            raise ValueError(
                f"the given start_node `{start_node.__qualname__}` is no component of this connection")
        if end_node is not None:
            if end_node not in (self.from_node_name, self.to_node_name):
                raise ValueError(
                    f"the given end_node `{end_node.__qualname__}` is no component of this connection")
        else:
            end_node = self.from_node_name if start_node == self.to_node_name else self.to_node_name

        if self.is_bidirectional():
            return True

        if start_node == self.from_node_name and end_node == self.to_node_name:
            return True

        return False

    def is_bidirectional(self) -> bool:
        """returns true if the gateway works in both directional"""
        return self._bidirectional
