from __future__ import annotations
from typing import TYPE_CHECKING, Type

import itertools

from .base_connection_relation import BaseConnectionRelation, BaseConnectionRelationT

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

    def get_possibilities_for_direct_parent_cnn(self, for_cnn_class: Type[Connection]) -> list[AndConnectionRelation]:
        """
        Helper method that returns a list of possible :class:`AndConnectionRelation` elements that hold the next parent
        in the connection-tree that can be there instead of the origin connection.
        The method returns a list, because there can exist different possibilities for this AND connection.
        """
        direct_ancestors_relations = ()
        for cur_and_elem in self.connections:
            # `cur_and_elem` needs to be a connection, because we are using simplified which has only
            # `OR[AND[Cnn, ...], Cnn, ..]`
            if cur_and_elem.__class__ in for_cnn_class.get_parents():
                # element already is a direct ancestor
                direct_ancestors_relations += (cur_and_elem,)
            else:
                all_pos_possibilities = []
                # add all possible direct parents to the possibilities list
                for cur_direct_parent in for_cnn_class.get_parents():
                    if cur_direct_parent.is_parent_of(cur_and_elem.__class__):
                        all_pos_possibilities.append(cur_direct_parent.based_on(cur_and_elem))
                direct_ancestors_relations += (all_pos_possibilities,)
        # resolve the opportunities and create multiple possible AND relations where all elements are
        # direct parents
        return [
            AndConnectionRelation(*cur_possibility).get_resolved()
            for cur_possibility in itertools.product(*direct_ancestors_relations)
        ]

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

    def cut_into_all_possible_subtree_branches(self) -> List[AndConnectionRelation]:
        if not self.is_single():
            raise ValueError('can not execute method, because relation is not single')

        tuple_with_all_possibilities = (
            tuple(cur_tuple_item.cut_into_all_possible_subtree_branches() for cur_tuple_item in self._connections))

        cloned_tuple_list = []
        for cur_tuple in list(itertools.product(*tuple_with_all_possibilities)):
            cloned_tuple = AndConnectionRelation(*[cur_tuple_item.clone() for cur_tuple_item in cur_tuple])
            cloned_tuple_list.append(cloned_tuple)
        return cloned_tuple_list

    def contained_in(self, other_conn: Union[Connection, BaseConnectionRelationT], ignore_metadata=False) -> bool:
        # This method checks if the AND relation is contained in the `other_conn`. To ensure that an AND relation is
        # contained in a connection tree, there has to be another AND relation into the `other_conn`, that has the same
        # length or is bigger. In addition, there has to exist an order combination where every element of the this AND
        # relation is contained in the found AND relation of the `other_cnn`. In this case it doesn't matter where the
        # AND relation is in `other_elem` (will be converted to single, and AND relation will be searched in all
        # BASED_ON elements). If the AND relation of `other_conn` has fewer items than this AND relation, it will be
        # ignored. The method only search for a valid existing item in the `other_conn` AND relation for every item of
        # this AND relation.
        from ..connection import Connection  # pylint: disable=import-outside-toplevel

        if not self.is_resolved():
            raise ValueError('can not execute method, because connection relation is not resolved')
        if not other_conn.is_resolved():
            raise ValueError('can not execute method, because other connection relation is not resolved')

        if isinstance(other_conn, BaseConnectionRelation):
            other_conn = Connection.based_on(other_conn)

        self_singles = self.get_singles()
        other_singles = other_conn.get_singles()

        for cur_self_single, cur_other_single in itertools.product(self_singles, other_singles):
            # check if we can find an AND relation in the other object -> go the single connection upwards and
            # search for a `AndConnectionRelation`

            # self is a container connection -> use raw inner AND list
            cur_self_single_and_relation = cur_self_single.based_on_elements.connections[0]

            cur_sub_other_single = cur_other_single
            while cur_sub_other_single is not None:
                if isinstance(cur_sub_other_single, AndConnectionRelation):
                    # found an AND relation -> check if length does match
                    if len(cur_sub_other_single) < len(cur_self_single_and_relation):
                        # this complete element is not possible - skip this single!
                        break
                    # length is okay, no check if every single element is contained in one of this tuple
                    for cur_inner_self_elem in cur_self_single_and_relation.connections:

                        if not cur_inner_self_elem.contained_in(cur_sub_other_single,
                                                                ignore_metadata=ignore_metadata):
                            # at least one element is not contained in other AND relation - this complete element
                            # is not possible - skip this single!
                            break
                    # all items are contained in the current other AND relation -> match
                    return True
                # go further up, if this element is no AND relation
                cur_sub_other_single = cur_sub_other_single.based_on_elements[0] \
                    if cur_sub_other_single.based_on_elements else None

        return False
