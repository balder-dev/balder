from __future__ import annotations
from typing import List, Tuple, Union, Type, Dict

import copy
import itertools

from _balder.connection_metadata import ConnectionMetadata
from _balder.device import Device
from _balder.exceptions import IllegalConnectionTypeError
from _balder.cnnrelations import AndConnectionRelation, OrConnectionRelation
from _balder.utils.functions import cnn_type_check_and_convert


class ConnectionType(type):
    """
    Metaclass for :class:`Connection` objects
    """

    def __and__(cls, other) -> AndConnectionRelation:
        return cls().__and__(other)

    def __or__(cls, other) -> OrConnectionRelation:
        return cls().__or__(other)


class Connection(metaclass=ConnectionType):
    """
    This is the basic connection class. On one side it is the common base class for all connection objects. On the other
    side it can also be used to describe a container connection, that contains a list of different connection items.
    """
    #: contains all parent connection information for every existing connection
    __parents: Dict[Type[Connection], Dict[str, List[Type[Connection]]]] = {}

    def __init__(self, from_device: Union[Type[Device], None] = None, to_device: Union[Type[Device], None] = None,
                 from_device_node_name: Union[str, None] = None, to_device_node_name: Union[str, None] = None):
        """
        This method creates a new Connection-Tree.

        .. note::
            With a direct instance of a :class:`Connection` object you can create an own Connection-Tree. You can use
            this container object, if you need a container for a list of :class:`Connection`-Trees that are combined
            with an AND (``&``) or/and an OR (``|``).

        :param from_device: the device this connection starts from (default: None)

        :param to_device: the device this connection ends in (default: None)

        :param from_device_node_name: the node name of the device the connection start

        :param to_device_node_name: the node name of the device the connection ends
        """
        # note: currently every connection is bidirectional (we want to add support for this later)

        # contains all metadata of this connection object
        self._metadata = ConnectionMetadata(
            from_device=from_device,
            to_device=to_device,
            from_device_node_name=from_device_node_name,
            to_device_node_name=to_device_node_name,
            bidirectional=True
        )

        # contains all sub connection objects, this connection tree is based on
        self._based_on_connections = OrConnectionRelation()

    def __and__(self, other: Union[Connection, AndConnectionRelation, OrConnectionRelation]) -> AndConnectionRelation:
        new_list = AndConnectionRelation(self)

        other = cnn_type_check_and_convert(other)
        new_list.append(other)

        return new_list

    def __or__(self, other: Union[Connection, AndConnectionRelation, OrConnectionRelation]) -> OrConnectionRelation:
        new_list = OrConnectionRelation(self)

        other = cnn_type_check_and_convert(other)
        new_list.append(other)

        return new_list

    def __eq__(self, other):
        if isinstance(other, Connection):
            return self.equal_with(other)

        return False

    def __hash__(self):
        all_hashes = hash(self.metadata) + hash(self.based_on_elements)
        return hash(all_hashes)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    @classmethod
    def get_parents(cls, tree_name: Union[str, None] = None) -> List[Type[Connection]]:
        """
        This method returns the parent classes of this connection.

        :param tree_name: the tree name the parents should be returned (default: use tree defined in `GlobalSetting`)
        """
        from _balder.balder_session import BalderSession  # pylint: disable=import-outside-toplevel
        if tree_name is None:
            tree_name = BalderSession.get_current_active_global_conntree_name()
        conn_dict = Connection.__parents.get(cls, {})
        parent_list = conn_dict.get(tree_name)
        return [] if parent_list is None else parent_list

    @classmethod
    def set_parents(cls, data: Union[List[Type[Connection]], None], tree_name: str = ""):
        """
        This method allows to set the data for the parent classes of this connection - note that None will remove the
        entry and completely disconnect this object from the global connection tree

        :param data: the new parents (None if everything should be reset)

        :param tree_name: the tree name of the parents that should be set (default: global tree)
        """
        if data is None:
            if cls in Connection.__parents.keys():
                if tree_name in Connection.__parents[cls].keys():
                    del Connection.__parents[cls][tree_name]
        else:
            if Connection.__parents.get(cls) is None:
                Connection.__parents[cls] = {}
            Connection.__parents[cls][tree_name] = data

    @classmethod
    def is_child_of(cls: Type[Connection], other_conn: Type[Connection]) -> bool:
        """
        determines whether this connection is a child of the given connection
        """
        return other_conn.is_parent_of(cls)

    @classmethod
    def is_parent_of(cls: Type[Connection], other_conn: Type[Connection]) -> bool:
        """
        determines whether this connection is a parent of the given connection
        """
        if other_conn.get_parents():
            if cls in other_conn.get_parents():
                return True
            for cur_higher_other_child in other_conn.get_parents():
                # ignore tuples, because this will return False (check with tuples not possible)
                if not isinstance(cur_higher_other_child, tuple):
                    if cls.is_parent_of(other_conn=cur_higher_other_child):
                        return True
            return False
        # the other connection has no parents, so this can not be the parent class
        return False

    @classmethod
    def based_on(
            cls,
            connection: Union[Connection, Type[Connection], AndConnectionRelation, OrConnectionRelation]
    ) -> Connection:
        """
        With this method it is possible to define several sublayers of the connection. You can pass various other
        connections in this method as arguments.

        Note that you can define logical statements with the `|` and the `&` operator.
        For example: ``Connection1() or Connection2() and Connection3()``.

        :param connection: all connection items for which this connection is based on

        """
        this_instance = cls()

        if isinstance(connection, type) and issubclass(connection, Connection):
            connection = connection()
        new_items = []
        if isinstance(connection, Connection):
            new_items.append(connection)
        elif isinstance(connection, AndConnectionRelation):
            new_items.append(connection)
        elif isinstance(connection, OrConnectionRelation):
            for cur_inner_elem in connection.connections:
                new_items.append(cur_inner_elem)
        else:
            raise TypeError(f'can not use object from type {connection}')

        # do not create a container connection if no container is required here
        if cls == Connection and len(new_items) == 1 and isinstance(new_items[0], Connection):
            return new_items[0]
        this_instance.append_to_based_on(*new_items)
        return this_instance

    @classmethod
    def filter_connections_that_are_contained_in(
            cls,
            cnns_from: List[Union[Connection, AndConnectionRelation, OrConnectionRelation]],
            are_contained_in: Connection,
            ignore_metadata: bool = False
    ) -> List[Connection]:
        """
        This method filters the connection elements from the first list to include only those connections that are
        contained within the provided connection ``are_contained_in``.

        :param cnns_from: a list of connections
        :param are_contained_in: the connection, the connection elements should be contained in
        :param ignore_metadata: True, if the metadata should be ignored
        :return: a list with the filtered connections
        """
        return [
            cnn for cnn in cnns_from
            if cnn.contained_in(other_conn=are_contained_in, ignore_metadata=ignore_metadata)
        ]

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def metadata(self) -> ConnectionMetadata:
        """returns the connection metadata dictionary"""
        return self._metadata

    @property
    def from_device(self):
        """device from which the connection starts"""
        return self._metadata.from_device if self._metadata else None

    @property
    def to_device(self):
        """device at which the connection ends"""
        return self._metadata.to_device if self._metadata else None

    @property
    def from_node_name(self):
        """the name of the node in the `Device` from which the connection starts"""
        return self._metadata.from_node_name if self._metadata else None

    @property
    def to_node_name(self):
        """the name of the node in the `Device` at which the connection ends"""
        return self._metadata.to_node_name if self._metadata else None

    @property
    def based_on_elements(self) -> OrConnectionRelation:
        """returns a copy of the internal based_on_connection"""
        return self._based_on_connections.clone()

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _is_directly_contained_in(self, other_conn: Connection, ignore_metadata: bool) -> bool:
        """
        Helper method that returns true if this connection is directly contained in the `other_conn`.

        .. note::
            'Directly contained-in' means that the resolved versions of both connections are of the same connection
            type, and the elements of that connection are directly embedded within one another from that point onward.
            It does not check deeper into the other_conn.

        :param other_conn: the other connection
        :param ignore_metadata: True, if the metadata should be ignored
        """

        resolved_self = self.get_resolved()
        resolved_other = other_conn.get_resolved()

        if resolved_self.__class__ == Connection and len(resolved_self.based_on_elements) == 0 or \
                resolved_other.__class__ == Connection and len(resolved_other.based_on_elements) == 0:
            # one of the resolved object is a raw `Connection` object without based-on-elements -> always true
            return True

        if resolved_self.__class__ == Connection:
            return resolved_self.based_on_elements.contained_in(resolved_other, ignore_metadata=ignore_metadata)

        if resolved_self.__class__ == resolved_other.__class__:
            # The element itself has already matched, now we still have to check whether at least one inner element
            # of this type is contained in minimum one element of the other
            singles_self = resolved_self.get_singles()
            singles_other = other_conn.get_singles()

            # check that for one single_self element all hierarchical based_on elements are in one of the single
            # other element
            for cur_single_self, cur_single_other in itertools.product(singles_self, singles_other):
                # check if both consists of only one element
                if len(cur_single_self.based_on_elements) == 0:
                    # the cur self single is only one element -> this is contained in the other
                    return True

                if len(cur_single_other.based_on_elements) == 0:
                    # the other element is only one element, but the self element not -> contained_in
                    # for this single definitely false
                    continue

                # note: for both only one `based_on_elements` is possible, because they are singles
                self_first_basedon = cur_single_self.based_on_elements[0]
                other_first_basedon = cur_single_other.based_on_elements[0]

                if isinstance(self_first_basedon, Connection) and \
                        isinstance(other_first_basedon, AndConnectionRelation):
                    continue

                # find a complete valid match
                if self_first_basedon.contained_in(other_first_basedon, ignore_metadata=ignore_metadata):
                    return True
        return False

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_intersection_with_other_single(
            self,
            other_conn: Union[Connection, AndConnectionRelation, OrConnectionRelation]
    ) -> List[Connection]:
        """
        A helper method that returns an intersection between the two connections (self and the given one).

        :param other_conn: the other **single** connection object (could be a relation too, but note that them needs to
                           be **single** elements!)
        """
        if not self.is_single():
            raise ValueError(
                "the current connection object is not single -> method only possible for single connections")
        if not other_conn.is_single():
            raise ValueError(
                "the other connection object is not single -> method only possible for single connections")

        intersection = []

        #: check if some sub elements of self connection are contained in `other_conn`
        self_pieces = self.cut_into_all_possible_pieces()
        intersection.extend(self.__class__.filter_connections_that_are_contained_in(
            cnns_from=self_pieces,
            are_contained_in=other_conn,
            ignore_metadata=True
        ))

        #: check if some sub elements of `other_conn` are contained in self connection
        other_pieces = other_conn.cut_into_all_possible_pieces()
        intersection.extend(self.__class__.filter_connections_that_are_contained_in(
            cnns_from=other_pieces,
            are_contained_in=self,
            ignore_metadata=True
        ))

        #: filter all duplicated (and contained in each other) connections
        intersection_without_duplicates = []
        for cur_conn in intersection:
            found_it = False
            for cur_existing_conn in intersection_without_duplicates:
                if cur_conn.equal_with(cur_existing_conn, ignore_metadata=True):
                    found_it = True
                    break
            if not found_it:
                intersection_without_duplicates.append(cur_conn)

        intersection_filtered = []
        #: filter all *contained in each other* connections
        for cur_conn in intersection_without_duplicates:
            is_contained_in_another = False
            for cur_validate_cnn in intersection_without_duplicates:
                if cur_validate_cnn == cur_conn:
                    # skip the same element
                    continue
                if cur_conn.contained_in(cur_validate_cnn, ignore_metadata=True):
                    is_contained_in_another = True
                    break
            if not is_contained_in_another:
                if isinstance(cur_conn, (AndConnectionRelation,OrConnectionRelation)):
                    cur_conn = Connection.based_on(cur_conn)
                intersection_filtered.append(cur_conn)

        # only return unique objects
        return intersection_filtered

    def clone_without_based_on_elements(self) -> Connection:
        """
        This method returns a copied version of this element, while all `_based_on_connections` are removed (the copied
        element has an empty list here).

        :return: a python copied object of this item
        """
        self_copy = copy.copy(self)
        self_copy._based_on_connections = OrConnectionRelation()  # pylint: disable=protected-access
        return self_copy

    def clone(self) -> Connection:
        """
        This method returns an exact clone of this connection. For this clone every inner connection object will be
        newly instantiated, but all internal references (like the devices and so on) will not be copied (objects are the
        same for this object and the clone). The method will make a normal copy for every connection object in the
        `_based_on_elements` list.
        """
        self_copy = self.clone_without_based_on_elements()
        self_copy.append_to_based_on(self._based_on_connections.clone())  # pylint: disable=protected-access
        return self_copy

    def cut_into_all_possible_subtree_branches(self) -> List[Connection]:
        """
        This method returns a list of all possible connection tree branches. A branch is a single connection, while
        this method returns a list of all possible singles where every single connection has this connection as head.
        """
        all_pieces = [self.clone()]
        if len(self.based_on_elements) == 0:
            return all_pieces

        if not self.is_single():
            raise ValueError("the current connection object is not single -> method only possible for single "
                             "connections")

        # return all possibilities of the relation while remain the current object as head
        for sub_branch in self.based_on_elements.cut_into_all_possible_subtree_branches():
            copied_conn = self.clone_without_based_on_elements()
            copied_conn.append_to_based_on(sub_branch)
            all_pieces.append(copied_conn)
        return all_pieces

    def cut_into_all_possible_pieces(self) -> List[Connection]:
        """
        This method cuts the resolved connection tree in all possible pieces by removing elements that change
        the existing tree - thereby the method returns a list with all possibilities (a copy of this object with all
        elements is contained too).

        .. note::
            Note that the given element or the child elements of a given direct :class:`Connection` object has to be
            single!
        """
        if self.__class__ == Connection:
            # this is only a container, execute process for every item of this one
            child_elems = self.based_on_elements.connections
        else:
            child_elems = [self]

        all_pieces = []

        for cur_item in child_elems:

            if not cur_item.is_single():
                raise ValueError("one of the given element is not single -> method only works with single items")

            cur_element = cur_item
            while cur_element:

                if isinstance(cur_element, AndConnectionRelation):
                    # now we can not go deeper, because we need this current AND connection
                    all_pieces += [Connection.based_on(and_relation)
                                   for and_relation in cur_element.cut_into_all_possible_subtree_branches()]
                    break

                all_pieces += cur_element.cut_into_all_possible_subtree_branches()

                if len(cur_element.based_on_elements.connections) > 1:
                    # should never be fulfilled because we have a single connection
                    raise ValueError('unexpected size of inner connections')

                cur_element = cur_element.based_on_elements.connections[0] \
                    if cur_element.based_on_elements.connections else None

        # filter all duplicates
        return list(set(all_pieces))

    def set_metadata_for_all_subitems(self, metadata: Union[ConnectionMetadata, None]):
        """
        This method sets the metadata for all existing Connection items in this element.

        :param metadata: the metadata that should be set (if the value is explicitly set to None, it removes the
                         metadata from every item)
        """
        if metadata is None:
            metadata = ConnectionMetadata()

        if not isinstance(metadata, ConnectionMetadata):
            raise TypeError('metadata must be an instance of `ConnectionMetadata`')

        for cur_base_elem in self._based_on_connections:
            cur_base_elem.set_metadata_for_all_subitems(metadata=metadata)
        self._metadata = metadata

    def get_tree_str(self) -> str:
        """
        This method returns a string, that represents all internal connections as readable string.

        :return: a readable string of the whole connection tree
        """
        if len(self.based_on_elements) == 0:
            return f"{self.__class__.__name__}()"

        based_on_strings = []
        for cur_elem in self.based_on_elements:
            if isinstance(cur_elem, tuple):
                based_on_strings.append(
                    f"({', '.join([cur_tuple_elem.get_tree_str() for cur_tuple_elem in cur_elem])})")
            else:
                based_on_strings.append(cur_elem.get_tree_str())

        return f"{self.__class__.__name__}.based_on({'| '.join(based_on_strings)})"

    def is_bidirectional(self) -> Union[bool, None]:
        """
        Provides the information in which direction the connection is supported (if the property returns true, the
        connection must work in both directions, otherwise it is a unidirectional connection from the `from_device` to
        the` to_device`
        """
        return self._metadata.bidirectional if self._metadata else None

    def is_universal(self):
        """
        Provides the information if the current connection object is a universal connection. This means, that the type
        is the base :class:`Connection` and the based_on_elements are empty.
        """
        return self.__class__ == Connection and len(self._based_on_connections) == 0

    def is_resolved(self):
        """
        This method returns true if the given (sub-)connection tree is completely resolved (describes every single
        Connection object of the tree - there are no undefined connection layers between an object and the given
        parent).
        """
        if self.__class__ == Connection:
            return self.based_on_elements.is_resolved()

        self_parents = self.__class__.get_parents()

        for cur_based_on in self.based_on_elements.connections:
            if isinstance(cur_based_on, Connection):
                if cur_based_on.__class__ not in self_parents:
                    return False
            elif isinstance(cur_based_on, (AndConnectionRelation, OrConnectionRelation)):
                for cur_type in cur_based_on.get_all_used_connection_types():
                    if cur_type not in self_parents:
                        return False
            if not cur_based_on.is_resolved():
                return False
        return True

    def is_single(self):
        """
        This method returns true if there exists no logical **OR** in the based on connection(s). One **AND** relation
        is allowed.

        .. note::
            Note that this method also returns False, if the connection is not completely resolved!
        """
        if len(self.based_on_elements) == 0:
            # tree ends here
            return True

        if len(self.based_on_elements) > 1:
            # more than one element -> not single
            return False

        if not self.is_resolved():
            return False

        return self.based_on_elements[0].is_single()

    def get_resolved(self) -> Connection:
        """
        This method returns a resolved Connection Tree. This means that it convert the based_on references so that
        every based on connection is a direct parent of the current element. It secures that there are no undefined
        connection layers between an object and the given parent.

        .. note::
            This method returns the connection without a container :class:`Connection`, if the container
            :class:`Connection` would only consist of one single connection (which is no AND relation!). In that case
            the method returns this child connection directly without any :class:`Connection` container otherwise the
            :class:`Connection` container class with all resolved child classes will be returned.
        """
        copied_base = self.clone_without_based_on_elements()

        if self.is_resolved():
            copied_base.append_to_based_on(self.based_on_elements.get_simplified_relation())
        elif self.__class__ == Connection:
            # the base object is a container Connection - iterate over the items and determine the values for them
            copied_base.append_to_based_on(self.based_on_elements.get_simplified_relation().get_resolved())
        else:
            # independent which based-on elements we have, we need to determine all elements between this connection
            # and the elements of the relation
            simplified_based_on = self.based_on_elements.get_simplified_relation()

            for next_higher_parent in simplified_based_on:
                if isinstance(next_higher_parent, AndConnectionRelation):
                    # determine all possibilities
                    for new_and_relation in next_higher_parent.get_possibilities_for_direct_parent_cnn(self.__class__):
                        copied_base.append_to_based_on(new_and_relation)
                else:
                    # `next_higher_parent` needs to be a connection, because we are using simplified which has only
                    # `OR[AND[Cnn, ...], Cnn, ..]`
                    if next_higher_parent.__class__ in self.__class__.get_parents():
                        # is already a direct parent
                        copied_base.append_to_based_on(next_higher_parent.get_resolved())
                        continue
                    # only add the first level of direct parents - deeper will be added by recursively call of
                    # `get_resolved`
                    for cur_self_direct_parent in self.__class__.get_parents():
                        if next_higher_parent.__class__.is_parent_of(cur_self_direct_parent):
                            new_child = cur_self_direct_parent.based_on(next_higher_parent)
                            copied_base.append_to_based_on(new_child.get_resolved())

        # if it is a connection container, where only one element exists that is no AND relation -> return this directly
        # instead of the container
        if copied_base.__class__ == Connection and len(copied_base.based_on_elements) == 1 and not \
                isinstance(copied_base.based_on_elements[0], AndConnectionRelation):
            return copied_base.based_on_elements[0]

        return copied_base

    def get_singles(self) -> List[Connection]:
        """
        This method returns a list with connection objects where every element is a single clear possibility of the
        current connection sub-tree. With this method the **OR** possibilities will be resolved, so that every item does
        not contain any OR relations.

        .. note::
            If the current object is a container :class:`Connection` object (direct instance of :class:`Connection`),
            this method returns the single elements without a container class!
        """
        # note: This method always work with the resolved and simplified version of the object because it is using
        # `get_resolved()`.
        if self.is_universal():
            return [self]

        if self.is_single():
            return [self]

        all_singles = []

        resolved_self = self.get_resolved()

        for cur_child in resolved_self.based_on_elements:
            for cur_single_child in cur_child.get_singles():
                cur_single_child = cur_single_child.clone()
                if self.__class__ == Connection and isinstance(cur_single_child, Connection):
                    all_singles.append(cur_single_child)
                else:
                    copied_base = resolved_self.clone_without_based_on_elements()
                    copied_base.append_to_based_on(cur_single_child)
                    all_singles.append(copied_base)

        return all_singles

    def get_conn_partner_of(self, device: Type[Device], node: Union[str, None] = None) -> Tuple[Type[Device], str]:
        """
        This method returns the connection partner of this connection - it always returns the other not given side

        :param device: the device itself - the other will be returned

        :param node: the node name of the device itself (only required if the connection starts and ends with the same
                     device)
        """
        return self.metadata.get_conn_partner_of(device, node)

    def has_connection_from_to(
            self,
            start_device: Type[Device],
            start_device_node_name: Union[str, None] = None,
            end_device: Union[Type[Device], None] = None,
            end_device_node_name: Union[str, None] = None,
    ) -> bool:
        """
        This method checks if there is a connection from ``start_device`` to ``end_device``. This will return
        true if the ``start_device`` and ``end_device`` given in this method are also the ``start_device`` and
        ``end_device`` mentioned in this connection object. If this is a bidirectional connection, ``start_device`` and
        ``end_device`` can switch places.


        :param start_device: the device for which the method should check whether it is a communication partner (for
                             non-bidirectional connection, this has to be the start device)
        :param start_device_node_name: the node name that start device should have or None if it should be ignored
        :param end_device: the other device for which the method should check whether it is a communication partner (for
                           non-bidirectional connection, this has to be the end device - this is optional if only the
                           start device should be checked)
        :param end_device_node_name: the node name that start device should have or None if it should be ignored

        :return: returns true if the given direction is possible
        """
        return self.metadata.has_connection_from_to(
            start_device=start_device,
            start_device_node_name=start_device_node_name,
            end_device=end_device,
            end_device_node_name=end_device_node_name
        )

    def equal_with(self, other_conn: Connection, ignore_metadata=False) -> bool:
        """
        This method returns True if the current object matches the given object. It always converts the elements to a
        resolved version and checks if both of them are exactly the same.

        .. note::
            Note that both Connection objects have to have the same ending parent elements. Only the order of the parent
            elements are obviously irrelevant.

        .. note::
            Note that it doesn't matter if the connection is embedded in a container-Connection element (direct
            instance of :class`Connection`) or not. It only checks, that the logical data of them are the same.

        :param other_conn: the other connection, this connection will be compared with

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: returns True if both elements are same
        """
        if not ignore_metadata:
            metadata_check_result = self.metadata.equal_with(other_conn.metadata)
            if metadata_check_result is False:
                return False

        # we do not need to check something for the container :class:`Connection`, because the `.get_resolved()` will
        # return no container if it only consists of one child connection
        resolved_self = self.get_resolved()
        resolved_other = other_conn.get_resolved()

        if self.__class__ != other_conn.__class__:
            return False

        return resolved_self.based_on_elements.equal_with(resolved_other.based_on_elements)

    def contained_in(
            self,
            other_conn: Connection | AndConnectionRelation | OrConnectionRelation,
            ignore_metadata=False
    ) -> bool:
        """
        This method determines if one connection tree can be embedded within another connection tree. A connection
        object represents a specific segment of the extensive connection tree managed by Balder. The method evaluates
        whether at least one SINGLE connection object of this connection tree fits within a possible SINGLE connection
        of the provided connection `other_conn`.

        .. note::
            The method returns true if one single connection of this object fits in another single connection that is
            given by `other_conn`.

        :param other_conn: the other connection

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: true if the self object is contained in the `other_conn`, otherwise false
        """
        # note: This method always work with the resolved and simplified version of the object because it is using
        # `get_resolved()`.

        if not ignore_metadata:
            metadata_check_result = self.metadata.contained_in(other_conn.metadata)
            if metadata_check_result is False:
                return False

        resolved_self = self.get_resolved()
        resolved_other = other_conn.get_resolved()

        if self._is_directly_contained_in(resolved_other, ignore_metadata=ignore_metadata):
            return True

        # the elements itself do not match -> go deeper within the other connection

        resolved_other_relation = resolved_other.based_on_elements \
            if isinstance(resolved_other, Connection) else resolved_other

        for cur_other_based_on in resolved_other_relation.connections:
            # `cur_other_based_on` can only be a Connection or an AND (resolved can not ba a inner OR)
            if isinstance(cur_other_based_on, AndConnectionRelation):
                # check if the current connection fits in one of the AND relation items -> allowed too (f.e. a
                # smaller AND contained in a bigger AND)
                for cur_other_and_element in cur_other_based_on.connections:
                    if resolved_self.contained_in(cur_other_and_element, ignore_metadata=ignore_metadata):
                        return True
            else:
                if resolved_self.contained_in(cur_other_based_on, ignore_metadata=ignore_metadata):
                    # element was found in this branch
                    return True
        return False

    def intersection_with(
            self, other_conn: Union[Connection, Type[Connection], AndConnectionRelation, OrConnectionRelation]) \
            -> Union[Connection, None]:
        """
        This method returns a list of subtrees that describe the intersection of this connection subtree and the
        given ones. Note that this method converts all connections in **single** **resolved** connections first.
        The method checks if there are common intersections between the elements of this object and the given connection
        elements within the single connections.
        The method cleans up this list and only return unique sub-connection trees!

        :param other_conn: the other sub connection tree list

        :return: the intersection connection or none, if the method has no intersection
        """
        other_conn = cnn_type_check_and_convert(other_conn)

        if isinstance(other_conn, Connection) and other_conn.__class__ == Connection:
            if len(other_conn.based_on_elements) == 0:
                return self.clone()
            other_conn = other_conn.based_on_elements

        if self.is_universal():
            return other_conn.clone() if isinstance(other_conn, Connection) else Connection.based_on(other_conn.clone())

        # determine all single connection of the two sides (could contain AND relations, where every element is a single
        # connection too)
        self_conn_singles = self.get_singles()
        other_conn_singles = other_conn.get_singles()

        intersections = []
        # determine intersections between all of these single components
        for cur_self_conn, cur_other_conn in itertools.product(self_conn_singles, other_conn_singles):
            for cur_intersection in cur_self_conn.get_intersection_with_other_single(cur_other_conn):
                intersections.append(cur_intersection)

        intersections = set(intersections)

        #: filter all *contained in each other* connections
        intersection_filtered = []
        for cur_conn in intersections:
            is_contained_in_another = False
            for cur_validate_cnn in intersections:
                if cur_validate_cnn == cur_conn:
                    # skip the same element
                    continue
                if cur_conn.contained_in(cur_validate_cnn, ignore_metadata=True):
                    is_contained_in_another = True
                    break
            if not is_contained_in_another:
                intersection_filtered.append(cur_conn)

        if len(intersection_filtered) == 0:
            # there is no intersection
            return None

        return Connection.based_on(OrConnectionRelation(*[cnn.clone() for cnn in intersection_filtered]))

    def append_to_based_on(
            self, *args: Union[Type[Connection], Connection, OrConnectionRelation, AndConnectionRelation]) -> None:
        """
        with this method you can extend the internal based_on list with the transferred elements. Any number of
        :meth:`Connection` objects or relations with :meth:`Connection` objects can be given to this method. They will
        all be added to the internal OR relation.

        :param args: all connection items that should be added here
        """

        def validate_that_subconnection_is_parent(idx, connection_type: Type[Connection]):
            if connection_type == Connection:
                raise ValueError(f"it is not allowed to provide a container Connection object in based_on items - "
                                 f"found at index {idx}")
            # `based_on` call for this sub-connection because we get an `Connection` object
            if self.__class__ != Connection:
                if not connection_type.is_parent_of(self.__class__):
                    raise IllegalConnectionTypeError(
                        f"the connection `{cur_elem.__class__.__name__}` (at parameter pos {idx}) is "
                        f"no parent class of the `{self.__class__.__name__}`")

        for cur_idx, cur_elem in enumerate(args):
            if isinstance(cur_elem, type) and issubclass(cur_elem, Connection):
                cur_elem = cur_elem()

            if isinstance(cur_elem, Connection):
                if cur_elem.is_universal():
                    # ignore it, because it is irrelevant for this connection
                    continue
                validate_that_subconnection_is_parent(cur_idx, cur_elem.__class__)
                self._based_on_connections.append(cur_elem)
            elif isinstance(cur_elem, OrConnectionRelation):
                for cur_inner_elem in cur_elem.connections:
                    if isinstance(cur_inner_elem, Connection) and cur_inner_elem.is_universal():
                        # ignore it, because it is irrelevant for this connection
                        continue
                    validate_that_subconnection_is_parent(cur_idx, cur_inner_elem.__class__)
                    self._based_on_connections.append(cur_inner_elem)
            elif isinstance(cur_elem, AndConnectionRelation):
                for cur_inner_type in cur_elem.get_all_used_connection_types():
                    validate_that_subconnection_is_parent(cur_idx, cur_inner_type)
                self._based_on_connections.append(cur_elem)
            else:
                raise TypeError(f"illegal type `{cur_elem.__name__}` for parameter at pos {cur_idx}")
