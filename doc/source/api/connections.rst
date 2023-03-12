Connections API
***************

:class:`Connection`'s will be used to connect :class:`Device`'s with each other. It does not matter whether
the device is a :class:`Scenario` device or a :class:`Setup` device.

Every connection object has to inherit from the class :class:`Connection` directly. It is important to note that
the connection tree is not realized via the normal Python inheritance, but by an internal representation. More details
see :ref:`Connections`.

Basic ``Connection``
====================

The basic :class:`Connection` class is the master class of every connection. It can always be used as container for
your sub-tree connection too.

.. autoclass:: balder.Connection
    :members:

OSI Layer 1: Physical Layer
===========================

.. autoclass:: balder.connections.BluetoothConnection
    :members:

.. autoclass:: balder.connections.CanBusConnection
    :members:

.. autoclass:: balder.connections.CoaxialCableConnection
    :members:

.. autoclass:: balder.connections.DslConnection
    :members:

.. autoclass:: balder.connections.RS232Connection
    :members:

.. autoclass:: balder.connections.RS422Connection
    :members:

.. autoclass:: balder.connections.RS485Connection
    :members:

.. autoclass:: balder.connections.IsdnConnection
    :members:

.. autoclass:: balder.connections.I2CConnection
    :members:

.. autoclass:: balder.connections.I2SConnection
    :members:

.. autoclass:: balder.connections.OneWireConnection
    :members:

.. autoclass:: balder.connections.OpticalFiberConnection
    :members:

.. autoclass:: balder.connections.SpiConnection
    :members:

.. autoclass:: balder.connections.TwistedPairCableConnection
    :members:

.. autoclass:: balder.connections.UsbConnection
    :members:

.. autoclass:: balder.connections.WifiConnection
    :members:

OSI Layer 2: Data Link Layer
============================

.. autoclass:: balder.connections.EthernetConnection
    :members:

.. autoclass:: balder.connections.WirelessLanConnection
    :members:

.. autoclass:: balder.connections.LLDPConnection
    :members:

.. autoclass:: balder.connections.ProfibusConnection
    :members:

OSI Layer 3: Network Layer
==========================

.. autoclass:: balder.connections.IpSecConnection
    :members:

.. autoclass:: balder.connections.IPv4Connection
    :members:

.. autoclass:: balder.connections.IPv6Connection
    :members:

.. autoclass:: balder.connections.IPConnection
    :members:

.. autoclass:: balder.connections.ICMPv4Connection
    :members:

.. autoclass:: balder.connections.ICMPv6Connection
    :members:

.. autoclass:: balder.connections.ICMPConnection
    :members:

OSI Layer 4: Transport Layer
============================

.. autoclass:: balder.connections.TcpIPv4Connection
    :members:

.. autoclass:: balder.connections.TcpIPv6Connection
    :members:

.. autoclass:: balder.connections.TcpConnection
    :members:

.. autoclass:: balder.connections.UdpIPv4Connection
    :members:

.. autoclass:: balder.connections.UdpIPv6Connection
    :members:

.. autoclass:: balder.connections.UdpConnection
    :members:

OSI Layer 4: Session Layer
==========================

.. autoclass:: balder.connections.PptpConnection
    :members:

OSI Layer 5: Presentation Layer
===============================

.. autoclass:: balder.connections.TelnetConnection
    :members:

OSI Layer 5: Application Layer
==============================

.. autoclass:: balder.connections.HttpConnection
    :members:

.. autoclass:: balder.connections.ImapConnection
    :members:

.. autoclass:: balder.connections.LdapConnection
    :members:

.. autoclass:: balder.connections.NtpConnection
    :members:

.. autoclass:: balder.connections.RpcConnection
    :members:

.. autoclass:: balder.connections.SmtpConnection
    :members:

.. autoclass:: balder.connections.SntpConnection
    :members:

.. autoclass:: balder.connections.SshConnection
    :members:

.. autoclass:: balder.connections.DnsConnection
    :members:
