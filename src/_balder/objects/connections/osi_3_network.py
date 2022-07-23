from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_2_datalink


@insert_into_tree(parents=[osi_2_datalink.EthernetConnection, osi_2_datalink.WirelessLanConnection])
class IPv4Connection(Connection):
    pass


@insert_into_tree(parents=[osi_2_datalink.EthernetConnection, osi_2_datalink.WirelessLanConnection])
class IPv6Connection(Connection):
    pass


IPConnection = Connection.based_on(IPv4Connection, IPv6Connection)


@insert_into_tree(parents=[IPv4Connection, IPv6Connection])
class IpSecConnection(Connection):
    pass


@insert_into_tree(parents=[IPv4Connection])
class ICMPv4Connection(Connection):
    pass


@insert_into_tree(parents=[IPv6Connection])
class ICMPv6Connection(Connection):
    pass


ICMPConnection = Connection.based_on(ICMPv4Connection, ICMPv6Connection)
