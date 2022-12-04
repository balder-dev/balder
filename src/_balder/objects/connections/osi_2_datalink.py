from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree

from _balder.objects.connections import osi_1_physical


@insert_into_tree(parents=[osi_1_physical.OpticalFiberConnection, osi_1_physical.DslConnection,
                           osi_1_physical.IsdnConnection])
class EthernetConnection(Connection):
    """
    Balder Ethernet connection (OSI LAYER 2)
    """


@insert_into_tree(parents=[osi_1_physical.WifiConnection])
class WirelessLanConnection(Connection):
    """
    Balder Wireless LAN connection (OSI LAYER 2)
    """


@insert_into_tree(parents=[])
class LLDPConnection(Connection):
    """
    Balder LLDP connection (OSI LAYER 2)
    """


@insert_into_tree(parents=[])
class ProfibusConnection(Connection):
    """
    Balder Profibus connection (OSI LAYER 2)
    """
