from __future__ import annotations
from typing import TYPE_CHECKING

from .base_connection_relation import BaseConnectionRelation

if TYPE_CHECKING:
    from ..connection import Connection


class OrConnectionRelation(BaseConnectionRelation):
    """
    describes a OR relation between connections
    """

    def get_tree_str(self) -> str:
        based_on_strings = [cur_elem.get_tree_str() for cur_elem in self._connections]
        return f"({' & '.join(based_on_strings)})"

    def get_simplified_relation(self) -> OrConnectionRelation:
        from ..connection import Connection  # pylint: disable=import-outside-toplevel

        result = OrConnectionRelation()
        for cur_inner_elem in self.connections:
            if isinstance(cur_inner_elem, Connection):
                # that is fine - just add it again
                result.append(cur_inner_elem)
            elif isinstance(cur_inner_elem, BaseConnectionRelation):
                # simplify this AND/OR relation and add the items of it
                # (the simplified version is always an OR relation!)
                result.extend(cur_inner_elem.get_simplified_relation())
            else:
                raise TypeError(f'detect unexpected element type `{cur_inner_elem.__class__}` in inner elements')
        return result
