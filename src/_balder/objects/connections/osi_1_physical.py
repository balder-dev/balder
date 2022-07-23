from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree


@insert_into_tree(parents=[])
class BluetoothConnection(Connection):
    pass


@insert_into_tree(parents=[])
class CanBusConnection(Connection):
    pass


@insert_into_tree(parents=[])
class CoaxialCableConnection(Connection):
    pass


@insert_into_tree(parents=[])
class DslConnection(Connection):
    pass


@insert_into_tree(parents=[])
class RS232Connection(Connection):
    pass


@insert_into_tree(parents=[])
class RS422Connection(Connection):
    pass


@insert_into_tree(parents=[])
class RS485Connection(Connection):
    pass


@insert_into_tree(parents=[])
class IsdnConnection(Connection):
    pass


@insert_into_tree(parents=[])
class I2CConnection(Connection):
    pass


@insert_into_tree(parents=[])
class I2SConnection(Connection):
    pass


@insert_into_tree(parents=[])
class OneWireConnection(Connection):
    pass


@insert_into_tree(parents=[])
class OpticalFiberConnection(Connection):
    pass


@insert_into_tree(parents=[])
class SpiConnection(Connection):
    pass


@insert_into_tree(parents=[])
class TwistedPairCableConnection(Connection):
    pass


@insert_into_tree(parents=[])
class UsbConnection(Connection):
    pass


@insert_into_tree(parents=[])
class WifiConnection(Connection):
    pass
