from __future__ import annotations

from _balder.objects.connections.osi_1_physical import BluetoothConnection, CanBusConnection, CoaxialCableConnection, \
    DslConnection, RS232Connection, RS422Connection, RS485Connection, IsdnConnection, I2CConnection, I2SConnection, \
    OneWireConnection, OpticalFiberConnection, SpiConnection, TwistedPairCableConnection, UsbConnection, WifiConnection
from _balder.objects.connections.osi_2_datalink import EthernetConnection, WirelessLanConnection, LLDPConnection, \
    ProfibusConnection
from _balder.objects.connections.osi_3_network import IpSecConnection, IPv4Connection, IPv6Connection, \
    ICMPv4Connection, ICMPv6Connection, IPConnection, ICMPConnection
from _balder.objects.connections.osi_4_transport import TcpIPv4Connection, UdpIPv4Connection, TcpIPv6Connection, \
    UdpIPv6Connection, TcpConnection, UdpConnection
from _balder.objects.connections.osi_5_session import PptpConnection
from _balder.objects.connections.osi_6_presentation import TelnetConnection
from _balder.objects.connections.osi_7_application import HttpConnection, ImapConnection, LdapConnection, \
    NtpConnection, RpcConnection, SmtpConnection, SntpConnection, SshConnection, DnsConnection

__all__ = [
    # OSI: Physical Layer
    "BluetoothConnection", "CanBusConnection", "CoaxialCableConnection", "DslConnection", "RS232Connection",
    "RS422Connection", "RS485Connection", "IsdnConnection", "I2CConnection", "I2SConnection", "OneWireConnection",
    "OpticalFiberConnection", "SpiConnection", "TwistedPairCableConnection", "UsbConnection", "WifiConnection",

    # OSI: Data Link Layer
    "EthernetConnection", "WirelessLanConnection", "LLDPConnection", "ProfibusConnection",

    # OSI: Network Layer
    "IpSecConnection", "IPv4Connection", "IPv6Connection", "ICMPv4Connection", "ICMPv6Connection",
    "IPConnection", "ICMPConnection",

    # OSI: Transport Layer
    "TcpIPv4Connection", "UdpIPv4Connection", "TcpIPv6Connection", "UdpIPv6Connection", "TcpConnection",
    "UdpConnection",

    # OSI: Session Layer
    "PptpConnection",

    # OSI Presentation Layer
    "TelnetConnection",

    # OSI Application Layer
    "HttpConnection", "ImapConnection", "LdapConnection", "NtpConnection", "RpcConnection",
    "SmtpConnection", "SntpConnection", "SshConnection", "DnsConnection"
]
