from __future__ import annotations
from typing import TYPE_CHECKING

import itertools

from .base_connection_relation import BaseConnectionRelation

if TYPE_CHECKING:
    from ..connection import List, Union, Connection
    from .or_connection_relation import OrConnectionRelation


class AndConnectionRelation(BaseConnectionRelation):
    """
    describes an AND relation between connections
    """

    def get_tree_str(self) -> str:
        based_on_strings = [cur_elem.get_tree_str() for cur_elem in self._connections]
        return f"({' | '.join(based_on_strings)})"

    def get_simplified_relation(self) -> OrConnectionRelation:
        from ..connection import Connection  # pylint: disable=import-outside-toplevel
        from .or_connection_relation import OrConnectionRelation  # pylint: disable=import-outside-toplevel

        # create template with all elements that are definitely contained in every new AND relation (only
        # ``Connection`` objects here)
        and_template = AndConnectionRelation()
        # add all OR relations that needs to be further resolved to that list
        self_simplified_or_relations = []

        # first: go through all inner elements and convert all relations in simplified relations
        for cur_elem in self.connections:
            if isinstance(cur_elem, Connection):
                # that is fine - add it to the template
                and_template.append(cur_elem)
            elif isinstance(cur_elem, (AndConnectionRelation, OrConnectionRelation)):
                # simplify this AND/OR relation and add the items of it
                # (the simplified version is always an OR relation!)
                self_simplified_or_relations.append(cur_elem.get_simplified_relation().connections)
            else:
                raise TypeError(f'unexpected type for inner element `{cur_elem}`')
        # now our `self_simplified_or_relations` can only consist of the following nesting: `List[OR[Conn, AND[Conn]]]`
        #  we need to resolve this constellation into `OR[Conn, AND[Conn]]` now

        # now generate all possibilities out of the OR relations and add them to the AND template
        all_new_ands = []
        for cur_variation_tuple in itertools.product(*self_simplified_or_relations):
            for cur_item in cur_variation_tuple:
                if isinstance(cur_item, Connection):
                    # just add the single connection item to the AND template
                    new_full_and_relation = and_template.clone()
                    new_full_and_relation.append(cur_item)
                    all_new_ands.append(new_full_and_relation)
                elif isinstance(cur_item, AndConnectionRelation):
                    new_full_and_relation = and_template.clone()
                    new_full_and_relation.extend(cur_item.connections)
                    all_new_ands.append(new_full_and_relation)
                else:
                    #: note: inner element can not be an OR here!
                    raise TypeError(f'detect illegal type `{cur_item.__class__}` for inner element')
        if not self_simplified_or_relations:
            all_new_ands.append(and_template)
        return OrConnectionRelation(*all_new_ands)

    def is_single(self) -> bool:

        if len(self._connections) == 0:
            return True

        return min(cnn.is_single() for cnn in self._connections)

    def get_singles(self) -> List[Connection]:
        from ..connection import Connection  # pylint: disable=import-outside-toplevel

        singles_and_relations = ()
        for cur_elem in self._connections:
            # get all singles of this AND relation element
            singles_and_relations += (cur_elem.get_singles(),)
        # now get the variations and add them to our results
        return [
            Connection.based_on(AndConnectionRelation(*cur_tuple))
            for cur_tuple in itertools.product(*singles_and_relations)
        ]
