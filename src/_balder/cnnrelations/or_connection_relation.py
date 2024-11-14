from __future__ import annotations

from .base_connection_relation import BaseConnectionRelation


class OrConnectionRelation(BaseConnectionRelation):

    def get_tree_str(self) -> str:
        based_on_strings = [cur_elem.get_tree_str() for cur_elem in self._connections]
        return f"({' & '.join(based_on_strings)})"
