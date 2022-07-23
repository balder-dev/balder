from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_3_network


@insert_into_tree(parents=[osi_3_network.IPv4Connection])
class TcpIPv4Connection(Connection):
    pass


@insert_into_tree(parents=[osi_3_network.IPv6Connection])
class TcpIPv6Connection(Connection):
    pass


TcpConnection = Connection.based_on(TcpIPv4Connection, TcpIPv6Connection)


@insert_into_tree(parents=[osi_3_network.IPv4Connection])
class UdpIPv4Connection(Connection):
    pass


@insert_into_tree(parents=[osi_3_network.IPv6Connection])
class UdpIPv6Connection(Connection):
    pass


UdpConnection = Connection.based_on(UdpIPv4Connection, UdpIPv6Connection)
