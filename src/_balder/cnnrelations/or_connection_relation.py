from __future__ import annotations
from typing import List, Union, TYPE_CHECKING

from .base_connection_relation import BaseConnectionRelation, BaseConnectionRelationT

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

    def is_single(self) -> bool:
        if len(self.connections) == 0:
            return True
        if len(self.connections) == 1:
            return self.connections[0].is_single()
        return False

    def get_singles(self) -> List[Connection]:
        result = []
        for elem in self.connections:
            result.extend(elem.get_singles())
        return result

    def cut_into_all_possible_subtree_branches(self) -> List[OrConnectionRelation]:
        if not self.is_single():
            raise ValueError('can not execute method, because relation is not single')
        result = [OrConnectionRelation()]
        if len(self.connections) == 0:
            return result
        result.extend(self.connections[0].cut_into_all_possible_subtree_branches())
        return result

    def contained_in(self, other_conn: Union[Connection, BaseConnectionRelationT], ignore_metadata=False) -> bool:
        if not self.is_resolved():
            raise ValueError('can not execute method, because connection relation is not resolved')
        if not other_conn.is_resolved():
            raise ValueError('can not execute method, because other connection relation is not resolved')
        for cur_inner_cnn in self._connections:
            if cur_inner_cnn.contained_in(other_conn, ignore_metadata=ignore_metadata):
                return True
        return False
