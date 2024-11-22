from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_3_network


@insert_into_tree(parents=[osi_3_network.IPv4Connection])
class TcpIPv4Connection(Connection):
    """
    Balder TCP IPv4 connection (OSI LAYER 4)
    """


@insert_into_tree(parents=[osi_3_network.IPv6Connection])
class TcpIPv6Connection(Connection):
    """
    Balder TCP IPv6 connection (OSI LAYER 4)
    """


TcpConnection = Connection.based_on(TcpIPv4Connection | TcpIPv6Connection)


@insert_into_tree(parents=[osi_3_network.IPv4Connection])
class UdpIPv4Connection(Connection):
    """
    Balder UDP IPv4 connection (OSI LAYER 4)
    """


@insert_into_tree(parents=[osi_3_network.IPv6Connection])
class UdpIPv6Connection(Connection):
    """
    Balder UDP IPv6 connection (OSI LAYER 4)
    """


UdpConnection = Connection.based_on(UdpIPv4Connection | UdpIPv6Connection)
