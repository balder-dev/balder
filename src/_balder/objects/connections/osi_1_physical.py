from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree


@insert_into_tree(parents=[])
class BluetoothConnection(Connection):
    """
    Balder Bluetooth connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class CanBusConnection(Connection):
    """
    Balder CAN-Bus connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class CoaxialCableConnection(Connection):
    """
    Balder Coaxial-Cable connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class DslConnection(Connection):
    """
    Balder DSL connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class RS232Connection(Connection):
    """
    Balder RS232 connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class RS422Connection(Connection):
    """
    Balder RS422 connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class RS485Connection(Connection):
    """
    Balder RS485 connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class IsdnConnection(Connection):
    """
    Balder ISDN connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class I2CConnection(Connection):
    """
    Balder I2C connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class I2SConnection(Connection):
    """
    Balder I2S connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class OneWireConnection(Connection):
    """
    Balder One-Wire connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class OpticalFiberConnection(Connection):
    """
    Balder Optical-Fiber connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class SpiConnection(Connection):
    """
    Balder SPI connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class TwistedPairCableConnection(Connection):
    """
    Balder Twisted-Pair Cable connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class UsbConnection(Connection):
    """
    Balder USB connection (OSI LAYER 1)
    """


@insert_into_tree(parents=[])
class WifiConnection(Connection):
    """
    Balder Wi-Fi connection (OSI LAYER 1)
    """
