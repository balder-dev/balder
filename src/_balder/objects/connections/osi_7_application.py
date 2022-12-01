from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_3_network, osi_4_transport


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class HttpConnection(Connection):
    """
    Balder HTTP connection (OSI LAYER 7)
    """


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class ImapConnection(Connection):
    """
    Balder IMAP connection (OSI LAYER 7)
    """


@insert_into_tree(
    parents=[
        (osi_4_transport.TcpIPv4Connection, osi_4_transport.UdpIPv4Connection),
        (osi_4_transport.TcpIPv6Connection, osi_4_transport.UdpIPv6Connection),
        osi_3_network.IPv4Connection,
        osi_3_network.IPv6Connection
    ])
class LdapConnection(Connection):
    """
    Balder LDAP connection (OSI LAYER 7)
    """


@insert_into_tree(parents=[osi_4_transport.UdpIPv4Connection, osi_4_transport.UdpIPv6Connection])
class NtpConnection(Connection):
    """
    Balder NTP connection (OSI LAYER 7)
    """


@insert_into_tree(
    parents=[
        (osi_4_transport.UdpIPv4Connection, osi_4_transport.TcpIPv4Connection),
        (osi_4_transport.UdpIPv6Connection, osi_4_transport.TcpIPv6Connection)
    ])
class RpcConnection(Connection):
    """
    Balder RPC connection (OSI LAYER 7)
    """


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class SmtpConnection(Connection):
    """
    Balder SMTP connection (OSI LAYER 7)
    """


@insert_into_tree(parents=[osi_4_transport.UdpIPv4Connection, osi_4_transport.UdpIPv6Connection])
class SntpConnection(Connection):
    """
    Balder SNTP connection (OSI LAYER 7)
    """


@insert_into_tree(parents=[osi_4_transport.TcpIPv4Connection, osi_4_transport.TcpIPv6Connection])
class SshConnection(Connection):
    """
    Balder SSH connection (OSI LAYER 7)
    """


@insert_into_tree(
    parents=[
        (osi_4_transport.UdpIPv4Connection, osi_4_transport.TcpIPv4Connection),
        (osi_4_transport.UdpIPv6Connection, osi_4_transport.TcpIPv6Connection)
    ])
class DnsConnection(Connection):
    """
    Balder DNS connection (OSI LAYER 7)
    """
