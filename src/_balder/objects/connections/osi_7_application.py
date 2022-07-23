from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_3_network, osi_4_transport


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class HttpConnection(Connection):
    pass


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class ImapConnection(Connection):
    pass


@insert_into_tree(
    parents=[
        (osi_4_transport.TcpIPv4Connection, osi_4_transport.UdpIPv4Connection),
        (osi_4_transport.TcpIPv6Connection, osi_4_transport.UdpIPv6Connection),
        osi_3_network.IPv4Connection,
        osi_3_network.IPv6Connection
    ])
class LdapConnection(Connection):
    pass


@insert_into_tree(parents=[osi_4_transport.UdpIPv4Connection, osi_4_transport.UdpIPv6Connection])
class NtpConnection(Connection):
    pass


@insert_into_tree(
    parents=[
        (osi_4_transport.UdpIPv4Connection, osi_4_transport.TcpIPv4Connection),
        (osi_4_transport.UdpIPv6Connection, osi_4_transport.TcpIPv6Connection)
    ])
class RpcConnection(Connection):
    pass


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class SmtpConnection(Connection):
    pass


@insert_into_tree(parents=[osi_4_transport.UdpIPv4Connection, osi_4_transport.UdpIPv6Connection])
class SntpConnection(Connection):
    pass


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class SshConnection(Connection):
    pass


@insert_into_tree(
    parents=[
        (osi_4_transport.UdpIPv4Connection, osi_4_transport.TcpIPv4Connection),
        (osi_4_transport.UdpIPv6Connection, osi_4_transport.TcpIPv6Connection)
    ])
class DnsConnection(Connection):
    pass
