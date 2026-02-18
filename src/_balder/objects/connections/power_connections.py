from __future__ import annotations

from _balder.connection import Connection
from _balder.decorator_insert_into_tree import insert_into_tree


@insert_into_tree(parents=[])
class PowerConnection(Connection):
    """
    Balder Electrical Power Wire Connection
    """

@insert_into_tree(parents=[PowerConnection])
class DCPowerConnection(Connection):
    """
    Balder Electrical Direct-Current (DC) Power Wire Connection
    """

@insert_into_tree(parents=[PowerConnection])
class ACPowerConnection(Connection):
    """
    Balder Electrical Alternating Current Power Wire Connection
    """
