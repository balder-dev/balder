from __future__ import annotations
from typing import TYPE_CHECKING

from .base_connection_relation import BaseConnectionRelation

if TYPE_CHECKING:
    from ..connection import Connection
    from .or_connection_relation import OrConnectionRelation


class AndConnectionRelation(BaseConnectionRelation):
    """
    describes an AND relation between connections
    """

    def get_tree_str(self) -> str:
        based_on_strings = [cur_elem.get_tree_str() for cur_elem in self._connections]
        return f"({' | '.join(based_on_strings)})"
