from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_4_transport


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class TelnetConnection(Connection):
    """
    Balder TELNET connection (OSI LAYER 6)
    """
