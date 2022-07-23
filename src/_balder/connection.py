from __future__ import annotations
from typing import List, Tuple, Union, Type, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.device import Device

import copy
import itertools

from _balder.exceptions import IllegalConnectionTypeError


class Connection:
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
            with an AND (tuple) or/and an OR (list).

        :param from_device: the device this connection starts from (default: None)

        :param to_device: the device this connection ends in (default: None)

        :param from_device_node_name: the node name of the device the connection start

        :param to_device_node_name: the node name of the device the connection ends
        """
        from _balder.device import Device

        # contains all metadata of this connection object
        self._metadata = {
            "from_device": None, "from_device_node_name": None, "to_device": None, "to_device_node_name": None
        }

        self._bidirectional = None
        # contains all sub connection objects, this connection tree is based on
        self._based_on_connections = []

        if from_device is not None and not issubclass(from_device, Device):
            raise TypeError(f"detect illegal argument element {str(from_device)} for given attribute "
                            f"`from_device` - should be a subclasses of `balder.Device`")
        self._metadata["from_device"] = from_device

        if from_device_node_name is not None and not isinstance(from_device_node_name, str):
            raise TypeError(f"detect illegal argument type {type(from_device_node_name)} for given attribute "
                            f"`from_device_node_name` - should be a string value")
        self._metadata["from_device_node_name"] = from_device_node_name

        if to_device is not None and not issubclass(to_device, Device):
            raise TypeError(f"detect illegal argument element {str(to_device)} for given attribute "
                            f"`to_device` - should be a subclasses of `balder.Device`")
        self._metadata["to_device"] = to_device

        if to_device_node_name is not None and not isinstance(to_device_node_name, str):
            raise TypeError(f"detect illegal argument type {type(to_device_node_name)} for given attribute "
                            f"`to_device_node_name` - should be a string value")
        self._metadata["to_device_node_name"] = to_device_node_name

        # describes if the connection is uni or bidirectional
        # note: currently every connection is bidirectional (we want to add support for this later)
        self._bidirectional = True

        if not ((from_device is None and to_device is None and from_device_node_name is None
                 and to_device_node_name is None) or (
                from_device is not None and to_device is not None and from_device_node_name is not None and
                to_device_node_name is not None)):
            raise ValueError(
                "you have to provide all or none of the following items: `from_device`, `from_device_node_name`, "
                "`to_device` or `to_device_node_name`")

    def __eq__(self, other):
        if isinstance(other, Connection):
            return self.equal_with(other)
        else:
            return False

    def __hash__(self):
        all_hashes = hash(self.from_device) + hash(self.to_device) + hash(self.from_node_name) + \
                     hash(self.to_node_name) + hash(str(self))
        for cur_child in self.based_on_elements:
            all_hashes += hash(cur_child)
        return hash(all_hashes)

    def clone(self) -> Connection:
        """
        This method returns an exact clone of this connection. For this clone every inner connection object will be
        newly instantiated, but all internal references (like the devices and so on) will not be copied (objects are the
        same for this object and the clone). The method will make a normal copy for every connection object in the
        `_based_on_elements` list.
        """
        self_copy = copy.copy(self)
        self_copy._based_on_connections = []

        for cur_based_on in self._based_on_connections:
            if isinstance(cur_based_on, tuple):
                cloned_tuple = ()
                for cur_tuple_element in cur_based_on:
                    cloned_tuple = cloned_tuple + (cur_tuple_element.clone(), )
                self_copy._based_on_connections.append(cloned_tuple)
            elif isinstance(cur_based_on, Connection):
                cloned_cur_based_on = cur_based_on.clone()
                self_copy._based_on_connections.append(cloned_cur_based_on)
            else:
                raise TypeError('based on element is not from valid type')
        return self_copy

    @staticmethod
    def __cut_conn_from_only_parent_to_child(elem: Connection) -> List[Connection]:
        """
        This helper method returns all possible pieces while the base element will remain intact - so every returned
        element is from the same type as `elem` (only the related `based_on_elements` are changed).

        .. note::
            The given element itself will also be added here!

        .. note::
            The given element has to be single!
        """
        all_pieces = [elem.clone()]
        if len(elem.based_on_elements) == 0:
            return all_pieces
        # if the next element is a tuple -> call procedure for tuples and add a copy of this object as child
        if isinstance(elem.based_on_elements[0], tuple):
            # return all possibilities of the tuple while adding the current object as child of the tuple
            for cur_tuple in Connection.__cut_tuple_from_only_parent_to_child(elem.based_on_elements[0]):
                # for this we do not have to use `clone`, because we copy the base object with `copy.copy` and
                # completely replace the `_based_on_connections` by our own
                copied_conn = copy.copy(elem)
                copied_conn._based_on_connections = [cur_tuple]
                all_pieces.append(copied_conn)
            return all_pieces
        # if this element is the last element with a parent -> copy it and remove the parent, return it
        if len(elem.based_on_elements[0].based_on_elements) == 0:
            new_elem = copy.copy(elem)
            new_elem._based_on_connections = []
            all_pieces.append(new_elem)
            return all_pieces
        # otherwise, the current item has grandparents, so call the method recursively for parents and add a copy of
        # this object as child
        all_possible_parents = Connection.__cut_conn_from_only_parent_to_child(elem.based_on_elements[0])
        for cur_parent in all_possible_parents:
            copied_conn = copy.copy(elem)
            copied_conn._based_on_connections = [cur_parent]
            all_pieces.append(copied_conn)
        return all_pieces

    @staticmethod
    def __cut_tuple_from_only_parent_to_child(elem: Tuple[Connection]) -> List[Tuple[Connection]]:
        """
        This helper method returns all possible pieces while the base elements of the tuple will remain intact - so
        every returned tuple element is from same type like the related elements in the tuple `elem` (only the related
        `based_on_elements` are changed).

        .. note::
            The given element has to be single!

        .. note::
            Note that this method also returns every possible ordering
        """

        tuple_with_all_possibilities = ()
        for cur_tuple_item in elem:
            tuple_with_all_possibilities += (Connection.__cut_conn_from_only_parent_to_child(cur_tuple_item), )

        cloned_tuple_list = []
        for cur_tuple in list(itertools.product(*tuple_with_all_possibilities)):
            cloned_tuple: Tuple[Connection] = ()
            for cur_tuple_item in cur_tuple:
                cloned_tuple += (cur_tuple_item.clone(), )
            cloned_tuple_list.append(cloned_tuple)
        return cloned_tuple_list

    @staticmethod
    def check_if_tuple_contained_in_connection(tuple_elem: Tuple[Connection], other_elem: Connection) -> bool:
        """
        This method checks if the tuple given by `tuple_elem` is contained in the `other_elem`. To ensure that a tuple
        element is contained in a connection tree, there has to be another tuple into the `other_elem`, that has the
        same length or is bigger. In addition, there has to exist an order combination where every element of the
        `tuple_elem` is contained in the found tuple in `other_elem`. In this case it doesn't matter where the tuple is
        in `other_elem` (will be converted to single, and tuple will be searched in all BASED_ON elements). If the tuple
        element of `other_elem` has fewer items than our `tuple_elem`, it will be ignored. The method only search for
        a valid existing item in the `other_elem` tuple for every item of the `tuple_elem`.

        :param tuple_elem: the tuple element that should be contained in the `other_elem`

        :param other_elem: the connection object, the given tuple should be contained in
        """
        def tuple_is_contained_in_other(inner_tuple, contained_in_tuple):
            # check if every tuple elem fits in one of `contained_in_tuple` (allow to use a position in
            # `contained_in_tuple` multiple times)
            for cur_idx in range(0, len(inner_tuple)):
                cur_tuple_element = inner_tuple[cur_idx]
                found_match_for_this_elem = False
                for cur_contained_in_elem in contained_in_tuple:
                    if cur_tuple_element.contained_in(cur_contained_in_elem, ignore_metadata=True):
                        found_match_for_this_elem = True
                        break
                if not found_match_for_this_elem:
                    return False
            return True

        other_singles = other_elem.get_singles()
        tuple_singles = Connection.convert_tuple_to_singles(tuple_elem)
        for cur_tuple_single in tuple_singles:
            for cur_other_single in other_singles:
                # check if we found a tuple element in the other object -> go the single connection upwards and search
                # for a tuple
                cur_sub_other_single: List[Union[Connection, Tuple[Connection]]] = [cur_other_single]
                while len(cur_sub_other_single) > 0:
                    if isinstance(cur_sub_other_single[0], tuple):
                        # found a tuple -> check if length does match
                        if len(cur_sub_other_single[0]) >= len(cur_tuple_single):
                            # length does match
                            if tuple_is_contained_in_other(
                                    cur_tuple_single, contained_in_tuple=cur_sub_other_single[0]):
                                return True
                        # otherwise, this complete element is not possible - skip this single!
                        break
                    cur_sub_other_single = cur_sub_other_single[0].based_on_elements
        return False

    @staticmethod
    def convert_tuple_to_singles(tuple_elem: Tuple[Connection]) -> List[Union[Connection, Tuple[Connection]]]:
        """
        This method converts the given `tuple_elem` to single items and return these.

        :param tuple_elem: the tuple element out of which the single items are being created

        :returns: a list of new connection objects that are single items
        """
        singles_tuple = ()
        tuple_idx = 0
        for cur_tuple_elem in tuple_elem:
            if not isinstance(cur_tuple_elem, Connection):
                raise TypeError(f"the tuple element at index {tuple_idx} of element from `other_conn` is not "
                                "from type `Connection`")
            # get all singles of this tuple element
            singles_tuple += (cur_tuple_elem.get_singles(),)
            tuple_idx += 1
        # now get the variations and add them to our results
        return list(itertools.product(*singles_tuple))

    @staticmethod
    def cleanup_connection_list(full_list: List[Union[Connection, Tuple[Connection]]]) \
            -> List[Union[Connection, Tuple[Connection]]]:
        """
        This method cleanup a connection list while removing items that are direct duplicates and by removing duplicates
        that are fully contained_in other items.

        :param full_list: the full list of connections and tuples of connections that should be cleaned-up

        :returns: returns the cleaned up list
        """
        result = full_list.copy()
        next_loop = True
        while not next_loop:
            next_loop = False
            for cur_elem in result:
                all_other_elems = [cur_item for cur_item in result if cur_item != cur_elem]
                if isinstance(cur_elem, Connection):
                    for cur_other_elem in all_other_elems:
                        # check if it contained in or the same
                        if cur_elem.contained_in(cur_other_elem, ignore_metadata=True):
                            # we can remove it from result list
                            result.remove(cur_elem)
                            next_loop = True
                            break
        return result

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    @classmethod
    def get_parents(cls, tree_name: Union[str, None] = None) -> List[Type[Connection]]:
        """
        This method returns the parent classes of this connection.

        :param tree_name: the tree name the parents should be returned (default: use tree defined in `GlobalSetting`)
        """
        from _balder.balder_session import BalderSession
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
        else:
            # the other connection has no parents, so this can not be the parent class
            return False

    @classmethod
    def based_on(cls, *args: Union[Tuple[Union[Type[Connection], Connection], ...], Type[Connection], Connection]) \
            -> Connection:
        """
        With this method it is possible to define several sublayers of the connection. You can pass various other
        connections in this method as arguments.

        Note that multiple parameters of this method (but also of all other methods that work with Connections) mean
        an OR operation. So if you define a `BaseConnType.based_on(ConnType1, ConnType2)` it means that your connection
        `BaseConnType` is based on a `ConnType1` or a `ConnType2`.

        In order to describe an AND operation, i.e. that the `BaseConnType` is based on a` ConnType1` and a `ConnType2`,
        you have to pass them as a tuple. This would look like this: `BaseConnType.based_on((ConnType1, ConnType2))`

        :param args: all connection items for which this connection is based on

        """
        this_instance = cls()

        new_items = []
        for cur_item in args:
            if isinstance(cur_item, Connection):
                if cur_item.__class__ == Connection:
                    # it is a container -> add elements
                    new_items += cur_item.based_on_elements
                else:
                    new_items.append(cur_item)
            elif isinstance(cur_item, type) and issubclass(cur_item, Connection):
                new_items.append(cur_item())
            else:
                new_items.append(cur_item)
        # do not create a container connection if no container is required here
        if cls == Connection and len(new_items) == 1 and not isinstance(new_items[0], tuple):
            return new_items[0]
        this_instance.append_to_based_on(*new_items)
        return this_instance

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, data):
        EMPTY_METADATA = {
            "from_device": None, "to_device": None, "from_device_node_name": None, "to_device_node_name": None}

        if not isinstance(data, dict):
            raise ValueError("the given metadata value has to be a dictionary")
        if data != {}:
            if sorted(["from_device", "to_device", "from_device_node_name", "to_device_node_name"]) != \
                    sorted(list(data.keys())):
                raise ValueError("if you provide a metadata dictionary you have to provide all elements of it")
        else:
            data = EMPTY_METADATA.copy()

        # only allow to set the metadata dictionary if the old one has the same values or was empty before (no values)
        if data != EMPTY_METADATA:
            if self._metadata == EMPTY_METADATA:
                # it is ok, because the dictionary was empty before
                pass
            elif self._metadata == data:
                # it is ok too, because the new set data is the same as the data was before
                pass
            else:
                raise ValueError("you can not set another metadata than the data set before - please reset it first")

        self._metadata = data

    @property
    def from_device(self):
        """device from which the connection starts"""
        return self._metadata["from_device"]

    @property
    def to_device(self):
        """device at which the connection ends"""
        return self._metadata["to_device"]

    @property
    def from_node_name(self):
        """the name of the node in the `Device` from which the connection starts"""
        return self._metadata["from_device_node_name"]

    @property
    def to_node_name(self):
        """the name of the node in the `Device` at which the connection ends"""
        return self._metadata["to_device_node_name"]

    @property
    def based_on_elements(self) -> List[Union[Connection, Tuple[Connection]]]:
        """returns a copy of the internal based_on_connection"""
        return self._based_on_connections.copy()

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _metadata_contained_in(self, of_connection: Connection) -> bool:
        """
        This method returns true if the metadata of the current connection is contained in the given one.

        The method returns true in the following situations:
        * both connections are bidirectional and the from and to elements (device and node name) are the same
        * both connections are unidirectional and have the same from and to elements
        * both connections are bidirectional and the from is the to and the to is the from
        * one connection is unidirectional and the other is bidirectional and the from and to elements are the same
        * one connection is unidirectional and the other is bidirectional and the from is the to and the to is the from

        :return: true if the metadata of the current connection is contained in the metadata of the given one
        """
        check_same = \
            self.from_device == of_connection.from_device and self.from_node_name == of_connection.from_node_name and \
            self.to_device == of_connection.to_device and self.to_node_name == of_connection.to_node_name
        check_opposite = \
            self.from_device == of_connection.to_device and self.from_node_name == of_connection.to_node_name and \
            self.to_device == of_connection.from_device and self.to_node_name == of_connection.from_node_name
        if self.is_bidirectional() and of_connection.is_bidirectional():
            return check_same or check_opposite
        elif self.is_bidirectional() and not of_connection.is_bidirectional() or \
                not self.is_bidirectional() and of_connection.is_bidirectional():
            return check_same or check_opposite
        else:
            return check_same

    def _metadata_equal_with(self, of_connection: Connection) -> bool:
        """
        This method returns true if the metadata of the current connection is equal with the metadata of the given
        connection.

        The method returns true in the following situations:
        * both connections are bidirectional and the from and to elements (device and node name) are the same
        * both connections are unidirectional and have the same from and to elements
        * both connections are bidirectional and the from is the to and the to is the from

        :return: true if the metadata of the current connection is contained in the metadata of the given one
        """
        check_same = \
            self.from_device == of_connection.from_device and self.from_node_name == of_connection.from_node_name and \
            self.to_device == of_connection.to_device and self.to_node_name == of_connection.to_node_name
        check_opposite = \
            self.from_device == of_connection.to_device and self.from_node_name == of_connection.to_node_name and \
            self.to_device == of_connection.from_device and self.to_node_name == of_connection.from_node_name
        if self.is_bidirectional() and of_connection.is_bidirectional() or \
                not self.is_bidirectional() and not of_connection.is_bidirectional():
            return check_same or check_opposite
        else:
            return False

    def _get_intersection_with_other_single(self, other_conn: Union[Connection, Tuple[Connection]]) \
            -> List[Connection, Tuple[Connection]]:
        """
        A helper method that returns an intersection between the two connections (self and the given one).

        :param other_conn: the other **single** connection object (could be a tuple too, but note that this has to have
                           only **single** elements!)
        """
        if not self.is_single():
            raise ValueError(
                "the current connection object is not single -> method only possible for single connections")
        if isinstance(other_conn, Connection):
            if other_conn.__class__ == Connection:
                raise ValueError("a container object from direct class `Connection` is not allowed here - please "
                                 "provide a single connection or a single tuple")
            if not other_conn.is_single():
                raise ValueError(
                    "the connection object given by `other_conn` is not single -> method only possible for single "
                    "connections")
        elif isinstance(other_conn, tuple):
            # has to be a tuple
            cur_idx = 0
            for cur_tuple_element in other_conn:
                if not cur_tuple_element.is_single():
                    raise ValueError(
                        f"the connection object given by tuple element at index {cur_idx} in `other_conn` is not "
                        f"single -> method only possible for single connections")
                cur_idx += 1
            other_conn = Connection.based_on(other_conn)
        else:
            raise TypeError("the object given by `other_conn` has to be from type `Connection` or has to be a tuple "
                            "of `Connection` objects")

        intersection = []

        #: check if some sub elements of self connection are contained in `other_conn`
        self_pieces = self.cut_into_all_possible_subtrees()
        for cur_piece in self_pieces:
            if isinstance(cur_piece, Connection):
                if cur_piece.contained_in(other_conn, ignore_metadata=True):
                    intersection.append(cur_piece)
            else:
                # isinstance of tuple
                if Connection.check_if_tuple_contained_in_connection(cur_piece, other_conn):
                    intersection.append(cur_piece)

        #: check if some sub elements of `other_conn` are contained in self connection
        other_pieces = other_conn.cut_into_all_possible_subtrees()
        for cur_piece in other_pieces:
            if isinstance(cur_piece, Connection):
                if cur_piece.contained_in(self, ignore_metadata=True):
                    intersection.append(cur_piece)
            else:
                # isinstance of tuple
                if Connection.check_if_tuple_contained_in_connection(cur_piece, self):
                    intersection.append(cur_piece)

        #: filter all duplicated (and contained in each other) connections
        intersection_without_duplicates = []
        for cur_conn in intersection:
            checkable_cur_conn = Connection.based_on(cur_conn) if isinstance(cur_conn, tuple) else cur_conn
            found_it = False
            for cur_existing_conn in intersection_without_duplicates:
                checkable_cur_existing_conn = Connection.based_on(cur_existing_conn) \
                    if isinstance(cur_existing_conn, tuple) else cur_existing_conn
                if checkable_cur_conn.equal_with(checkable_cur_existing_conn, ignore_metadata=True):
                    found_it = True
                    break
            if not found_it:
                intersection_without_duplicates.append(cur_conn)
        intersection_filtered = []
        #: filter all *contained in each other* connections
        for cur_conn in intersection_without_duplicates:
            usable_cur_conn = Connection.based_on(cur_conn) if isinstance(cur_conn, tuple) else cur_conn
            is_contained_in_another = False
            for cur_validate_cnn in intersection_without_duplicates:
                if cur_validate_cnn == cur_conn:
                    # skip the same element
                    continue
                if usable_cur_conn.contained_in(cur_validate_cnn, ignore_metadata=True):
                    is_contained_in_another = True
                    break
            if not is_contained_in_another:
                intersection_filtered.append(cur_conn)

        # only return unique objects
        return intersection_filtered

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def set_devices(self, from_device: Type[Device], to_device: Type[Device]):
        """
        Method for setting the devices of the connection if this has not yet been done during instantiation

        .. note::
            Note that you can not change the devices after they were set (only possible internally)

        :param from_device: device from which the connection starts

        :param to_device: device at which the connection ends
        """
        if self.from_device is not None or self.to_device is not None:
            raise ValueError("devices already set")
        self._metadata["from_device"] = from_device
        self._metadata["to_device"] = to_device

    def update_node_names(self, from_device_node_name: str, to_device_node_name: str) -> None:
        """
        This method dates the names of the nodes from which the connection in the `from_device` originates and finally
        arrives in the` to_device`. Please provide the node name of your ``from_device`` in ``from_device_node_name``
        and the node name of your ``to_device`` in ``to_device_node_name``.

        :param from_device_node_name: specifies the node in the ``from_device``

        :param to_device_node_name: specifies the node in the ``to_device``
        """
        self._metadata["from_device_node_name"] = from_device_node_name
        self._metadata["to_device_node_name"] = to_device_node_name

    def cut_into_all_possible_subtrees(self) -> List[Union[Connection, Tuple[Connection]]]:
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
            child_elems = self.based_on_elements
        else:
            child_elems = [self]

        all_pieces = []

        for cur_item in child_elems:

            if isinstance(cur_item, Connection):
                if not cur_item.is_single():
                    raise ValueError("one of the given element is not single -> method only works with single items")
            elif isinstance(cur_item, tuple):
                tuple_idx = 0
                for cur_tuple_elem in cur_item:
                    if not cur_tuple_elem.is_single():
                        raise ValueError(
                            f"one of the given tuple element has a item at index {tuple_idx}, that is not single -> "
                            f"method only works with single items or tuple of single items")
                    tuple_idx += 1

            cur_element = [cur_item]
            while len(cur_element) > 0:
                if isinstance(cur_element[0], Connection):
                    all_pieces += Connection.__cut_conn_from_only_parent_to_child(cur_element[0])
                elif isinstance(cur_element[0], tuple):
                    all_pieces += Connection.__cut_tuple_from_only_parent_to_child(cur_element[0])
                    # now we can not go deeper, because we need this current AND connection
                    break
                cur_element = cur_element[0].based_on_elements

        # filter all duplicates
        return list(set(all_pieces))

    def set_metadata_for_all_subitems(self, metadata: Union[Dict[str, Union[Device, str]], None]):
        """
        This method sets the metadata for all existing Connection items in this element.

        :param metadata: the metadata that should be set (if the value is explicitly set to None, it removes the
                         metadata from every item)
        """
        if metadata is None:
            metadata = {
                "from_device": None, "to_device": None, "from_device_node_name": None, "to_device_node_name": None}

        for cur_base_elem in self._based_on_connections:
            if isinstance(cur_base_elem, Connection):
                cur_base_elem.set_metadata_for_all_subitems(metadata=metadata)
            elif isinstance(cur_base_elem, tuple):
                for cur_tuple_elem in cur_base_elem:
                    cur_tuple_elem.set_metadata_for_all_subitems(metadata=metadata)
            else:
                raise TypeError(
                    f"found illegal type {cur_base_elem.__class__} for based_on item at index {cur_base_elem}")
        self.metadata = metadata

    def get_tree_str(self) -> str:
        """
        This method returns a string, that represents all internal connections as readable string.

        :return: a readable string of the whole connection tree
        """
        if len(self.based_on_elements) == 0:
            return f"{self.__class__.__name__}()"
        else:
            based_on_strings = []
            for cur_elem in self.based_on_elements:
                if isinstance(cur_elem, tuple):
                    based_on_strings.append(
                        f"({', '.join([cur_tuple_elem.get_tree_str() for cur_tuple_elem in cur_elem])})")
                else:
                    based_on_strings.append(cur_elem.get_tree_str())

            return f"{self.__class__.__name__}.based_on({', '.join(based_on_strings)})"

    def is_bidirectional(self):
        """
        Provides the information in which direction the connection is supported (if the property returns true, the
        connection must work in both directions, otherwise it is a unidirectional connection from the `from_device` to
        the` to_device`
        """
        return self._bidirectional

    def is_universal(self):
        """
        Provides the information if the current connection object is a universal connection. This means, that the type
        is the base :class:`Connection` and the based_on_elements are empty.
        """
        return type(self) == Connection and len(self._based_on_connections) == 0

    def is_resolved(self):
        """
        This method returns true if the given (sub-)connection tree is completely resolved (describes every single
        Connection object of the tree - there are no undefined connection layers between an object and the given
        parent).
        """
        for cur_based_on in self.based_on_elements:
            if isinstance(cur_based_on, tuple):
                for cur_tuple_elem in cur_based_on:
                    # check the next parent class type only if the main self type is not a container
                    # (base `balder.Connection` object)
                    if self.__class__ != Connection:
                        if cur_tuple_elem not in self.__class__.get_parents():
                            # only one element is not directly parent -> return false
                            return False
                    if not cur_tuple_elem.is_resolved():
                        # only one subelement is not resolved -> return false
                        return False
            else:
                # no tuple, single element

                # check the next parent class type only if the main self type is not a container
                # (base `balder.Connection` object)
                if self.__class__ != Connection:
                    if cur_based_on.__class__ not in self.__class__.get_parents():
                        # only one element is not directly parent -> return false
                        return False
                if not cur_based_on.is_resolved():
                    # only one subelement is not resolved -> return false
                    return False
        return True

    def is_single(self):
        """
        This method returns true if there exists no logical **OR** in the based on connection(s). One **AND** tuple is
        allowed.

        .. note::
            Note that this method also returns False, if the connection is not completely resolved!
        """
        if len(self.based_on_elements) == 0:
            # tree ends here
            return True
        elif len(self.based_on_elements) > 1:
            # more than one element -> not single
            return False

        if not self.is_resolved():
            return False

        if isinstance(self.based_on_elements[0], tuple):
            for cur_tuple_elem in self.based_on_elements[0]:
                # if only one element of tuple is not single -> return False
                if not cur_tuple_elem.is_single():
                    return False
            # all elements are single
            return True
        else:
            return self.based_on_elements[0].is_single()

    def get_resolved(self) -> Connection:
        """
        This method returns a resolved Connection Tree. This means that it convert the based_on references so that
        every based on connection is a direct parent of the current element. It secures that there are no undefined
        connection layers between an object and the given parent.

        .. note::
            This method returns the connection without a container :class:`Connection`, if the container
            :class:`Connection` would only consist of one single connection (which is no tuple!). In this case the
            method returns this child connection directly without any :class:`Connection` container otherwise the
            :class:`Connection` container class with all resolved child classes will be returned.
        """
        copied_base = copy.copy(self)
        if not copied_base.is_resolved():
            copied_base._based_on_connections = []
            if self.__class__ == Connection:
                # the base object is a container Connection - iterate over the items and determine the values for them
                for cur_item in self.based_on_elements.copy():
                    if isinstance(cur_item, tuple):
                        new_tuple = ()
                        for cur_tuple_item in cur_item:
                            new_tuple += (cur_tuple_item.get_resolved(), )
                        copied_base._based_on_connections.append(new_tuple)
                    else:
                        copied_base._based_on_connections.append(cur_item.get_resolved())
            else:
                for next_higher_parent in self.based_on_elements:
                    if isinstance(next_higher_parent, tuple):
                        # determine all possibilities
                        direct_ancestors_tuple = ()
                        for cur_tuple_elem in next_higher_parent:
                            if cur_tuple_elem.__class__ in self.__class__.get_parents():
                                # element already is a direct ancestor
                                direct_ancestors_tuple += (cur_tuple_elem, )
                            else:
                                all_pos_possibilities = []
                                # add all possible direct parents to the possibilities list
                                for cur_direct_parent in self.__class__.get_parents():
                                    if cur_direct_parent.is_parent_of(cur_tuple_elem.__class__):
                                        all_pos_possibilities.append(cur_direct_parent.based_on(cur_tuple_elem))
                                direct_ancestors_tuple += (all_pos_possibilities, )
                        # resolve the opportunities and create multiple possible tuples where all elements are direct
                        # parents
                        for cur_possibility in itertools.product(*direct_ancestors_tuple):
                            new_child_tuple = ()
                            for cur_tuple_element in cur_possibility:
                                new_child_tuple += (cur_tuple_element.get_resolved(), )
                            copied_base._based_on_connections.append(new_child_tuple)
                    else:
                        if next_higher_parent.__class__ in self.__class__.get_parents():
                            # is already a direct parent
                            copied_base._based_on_connections.append(next_higher_parent.get_resolved())
                        else:
                            # only add the first level of direct parents - deeper will be added by recursively call of
                            # `get_resolved`
                            for cur_self_direct_parent in self.__class__.get_parents():
                                if next_higher_parent.__class__.is_parent_of(cur_self_direct_parent):
                                    new_child = cur_self_direct_parent.based_on(next_higher_parent)
                                    copied_base._based_on_connections.append(new_child.get_resolved())
        # if it is a connection container, where only one element exists that is no tuple -> return this directly
        # instead of the container
        if copied_base.__class__ == Connection and len(copied_base.based_on_elements) == 1 and not \
                isinstance(copied_base.based_on_elements[0], tuple):
            return copied_base.based_on_elements[0]
        else:
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
        all_singles = []

        all_self_items = [self]
        if self.__class__ == Connection and len(self.based_on_elements) == 0:
            return [self]
        if self.__class__ == Connection:
            all_self_items = self.based_on_elements
        for cur_item in all_self_items:
            if isinstance(cur_item, tuple):
                all_singles += Connection.convert_tuple_to_singles(cur_item)
            elif cur_item.is_single():
                all_singles.append(copy.copy(cur_item))
            else:
                # do this for resolved version of this object
                resolved_obj = cur_item.get_resolved()

                if len(resolved_obj.based_on_elements) == 0:
                    # element has no children -> return only this
                    return [resolved_obj]
                for cur_child in resolved_obj.based_on_elements:
                    for cur_single_child in cur_child.get_singles():
                        copied_base = copy.copy(resolved_obj)
                        copied_base._based_on_connections = [cur_single_child]
                        all_singles.append(copied_base)
        # convert all tuple objects in a connection object and set metadata of self object
        cleaned_singles = []

        for cur_single in all_singles:
            if isinstance(cur_single, Connection):
                new_cnn = cur_single
            else:
                new_cnn = Connection.based_on(cur_single)

            new_cnn.set_metadata_for_all_subitems(self.metadata)
            cleaned_singles.append(new_cnn)
        return cleaned_singles

    def get_conn_partner_of(self, device: Type[Device], node: Union[str, None] = None) -> Tuple[Type[Device], str]:
        """
        This method returns the connection partner of this connection - it always returns the other not given side

        :param device: the device itself - the other will be returned

        :param node: the node name of the device itself (only required if the connection starts and ends with the same
                     device)
        """
        if device != self.from_device and device != self.to_device:
            raise ValueError(f"the given device `{device.__qualname__}` is no component of this connection")
        if node is None:
            # check that the from_device and to_device are not the same
            if self.from_device == self.to_device:
                raise ValueError("the connection is a inner-device connection (start and end is the same device) - you "
                                 "have to provide the `node` string too")
            if device == self.from_device:
                return self.to_device, self.to_node_name
            else:
                return self.from_device, self.from_node_name
        else:
            if node != self.from_node_name and node != self.to_node_name:
                raise ValueError(f"the given node `{node}` is no component of this connection")

            if device == self.from_device and node == self.from_node_name:
                return self.to_device, self.to_node_name
            elif device == self.to_device and node == self.to_node_name:
                return self.from_device, self.from_node_name
            else:
                raise ValueError(f"the given node `{node}` is no component of the given device `{device.__qualname__}`")

    def has_connection_from_to(self, start_device, end_device=None):
        """
        This method checks if there is a connection from ``start_device`` to ``end_device``. This will return
        true if the ``start_device`` and ``end_device`` given in this method are also the ``start_device`` and
        ``end_device`` mentioned in this connection object. If this is a bidirectional connection, ``start_device`` and
        ``end_device`` can switch places.


        :param start_device: the device for which the method should check whether it is a communication partner (for
                             non-bidirectional connection, this has to be the start device)

        :param end_device: the other device for which the method should check whether it is a communication partner (for
                           non-bidirectional connection, this has to be the end device - this is optional if only the
                           start device should be checked)

        :return: returns true if the given direction is possible
        """
        if end_device is None:

            if self.is_bidirectional():
                return start_device == self.from_device or start_device == self.to_device
            else:
                return start_device == self.from_device
        else:
            if self.is_bidirectional():
                return start_device == self.from_device and end_device == self.to_device or \
                       start_device == self.to_device and end_device == self.from_device
            else:
                return start_device == self.from_device and end_device == self.to_device

    def equal_with(self, other_conn: Connection, ignore_metadata=False) -> bool:
        """
        This method returns True if the current object matches the given object. It always converts the elements to a
        resolved version and checks if both of them are exactly the same.

        .. note::
            Note that both Connection objects have to have the same ending parent elements. Only the order of the parent
            elements are obviously irrelevant.

        .. note::
            Note that it doesn't matter if the connection is embedded in a container-Connection element (direct
            instance of :class`Connection`) or not. It only checks, that the logical data of them are the same. If both
            elements are a container for a list of child connections, the method secures that both has the same
            children. If only one (same for both) has one child connection which is embedded in a container
            :class:`Connection` class, it returns also true if the other connection is like the one child element of
            the other container :class:`Connection`.

        :param other_conn: the other connection, this connection will be compared with

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: returns True if both elements are same
        """
        if self.__class__ != Connection and self.__class__ != other_conn.__class__:
            return False

        if not ignore_metadata:
            metadata_check_result = self._metadata_equal_with(of_connection=other_conn)
            if metadata_check_result is False:
                return False

        # we do not need to check something for the container :class:`Connection`, because the `.get_resolved()` will
        # return no container if it only consists of one child connection
        resolved_self = self.get_resolved()
        resolved_other = other_conn.get_resolved()

        def check_elems_if(elems_from, are_in_elems_from):
            for cur_elem in elems_from:
                found_equal = False
                for cur_other_elem in are_in_elems_from:
                    if cur_elem.equal_with(cur_other_elem, ignore_metadata=ignore_metadata):
                        found_equal = True
                        break
                if not found_equal:
                    return False
            return True

        def check_tuples_if(tuples_from, are_in_tuples_from):
            for cur_search_tuple in tuples_from:
                found_match_for_cur_search_tuple = False
                # go through each unmatched other tuple
                for cur_other_tuple in are_in_tuples_from:
                    cur_search_tuple_is_completely_in_other_tuple = True
                    for cur_search_tuple_elem in cur_search_tuple:
                        fount_it = False
                        for cur_other_tuple_elem in cur_other_tuple:
                            if cur_search_tuple_elem.equal_with(cur_other_tuple_elem, ignore_metadata=ignore_metadata):
                                fount_it = True
                                break
                        if not fount_it:
                            cur_search_tuple_is_completely_in_other_tuple = False
                            break
                    if cur_search_tuple_is_completely_in_other_tuple:
                        # here we have no match
                        found_match_for_cur_search_tuple = True
                        break
                if not found_match_for_cur_search_tuple:
                    return False
            return True

        self_based_on_elems = [
            cur_elem for cur_elem in resolved_self.based_on_elements if isinstance(cur_elem, Connection)]
        self_based_on_tuples = [
            cur_elem for cur_elem in resolved_self.based_on_elements if isinstance(cur_elem, tuple)]
        other_based_on_elems = [
            cur_elem for cur_elem in resolved_other.based_on_elements if isinstance(cur_elem, Connection)]
        other_based_on_tuples = [
            cur_elem for cur_elem in resolved_other.based_on_elements if isinstance(cur_elem, tuple)]

        # check single connection elements (if they match all in both directions)
        if not check_elems_if(elems_from=self_based_on_elems, are_in_elems_from=other_based_on_elems):
            return False
        if not check_elems_if(elems_from=other_based_on_elems, are_in_elems_from=self_based_on_elems):
            return False

        # check tuple connection elements (if they match all in both directions)
        if not check_tuples_if(tuples_from=self_based_on_tuples, are_in_tuples_from=other_based_on_tuples):
            return False
        if not check_tuples_if(tuples_from=other_based_on_tuples, are_in_tuples_from=self_based_on_tuples):
            return False

        return True

    def contained_in(self, other_conn: Connection, ignore_metadata=False) -> bool:
        """
        This method helps to find out whether this connection-tree fits within a given connection tree. A connection
        object is a certain part of the large connection tree that Balder has at its disposal. This method checks
        whether a possibility of this connection tree fits in one possibility of the given connection tree.

        .. note::
            The method returns true if one single connection of this object fits in another single connection that is
            given by `other_conn`.

        :param other_conn: the other connection

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: true if the self object is contained in the `other_conn`, otherwise false
        """
        if not ignore_metadata:
            metadata_check_result = self._metadata_contained_in(of_connection=other_conn)
            if metadata_check_result is False:
                return False

        resolved_self = self.get_resolved()
        resolved_other = other_conn.get_resolved()

        if resolved_self.__class__ == Connection and len(resolved_self.based_on_elements) == 0 or \
                resolved_other.__class__ == Connection and len(resolved_other.based_on_elements) == 0:
            # one of the resolved object is a raw `Connection` object without based-on-elements -> always true
            return True

        self_possibilities = [resolved_self]
        if resolved_self.__class__ == Connection:
            self_possibilities = resolved_self.based_on_elements
        for cur_self in self_possibilities:
            if isinstance(cur_self, tuple):
                if Connection.check_if_tuple_contained_in_connection(cur_self, resolved_other):
                    return True
            elif not cur_self.__class__ == resolved_other.__class__:
                for cur_based_on_elem in resolved_other.based_on_elements:
                    if isinstance(cur_based_on_elem, tuple):
                        # check if the current connection fits in one of the tuple items -> allowed too (like a smaller
                        # AND contained in a bigger AND)
                        for cur_other_tuple_element in cur_based_on_elem:
                            if cur_self.contained_in(cur_other_tuple_element, ignore_metadata=ignore_metadata):
                                return True
                    else:
                        if cur_self.contained_in(cur_based_on_elem, ignore_metadata=ignore_metadata):
                            # element was found in this branch
                            return True
            else:
                # The element itself has already matched, now we still have to check whether at least one tuple or a
                # connection (i.e. one element of the list) is matched with one of the other
                singles_self = cur_self.get_singles()
                singles_other = resolved_other.get_singles()

                # check that for one single_self element all hierarchical based_on elements are in one of the single
                # other element
                for cur_single_self in singles_self:
                    for cur_single_other in singles_other:
                        # check if both consists of only one element
                        if len(cur_single_self.based_on_elements) == 0:
                            # the cur self single is only one element -> this is contained in the other
                            return True
                        elif len(cur_single_other.based_on_elements) == 0:
                            # the other element is only one element, but the self element not -> contained_in
                            # for this single definitely false
                            continue
                        # note: for both only one `based_on_elements` is possible, because they are singles
                        if isinstance(cur_single_self.based_on_elements[0], tuple) and \
                                isinstance(cur_single_other.based_on_elements[0], tuple):
                            # both are tuples -> check that there exist a matching where all are contained_in
                            tuple_is_complete_contained_in = True
                            # check that every tuple element of self is contained in minimum one tuple elements of each
                            # other
                            for cur_self_tuple_element in cur_single_self.based_on_elements[0]:
                                find_some_match_for_cur_self_tuple_element = False
                                for cur_other_tuple_element in cur_single_other.based_on_elements[0]:
                                    if cur_self_tuple_element.contained_in(
                                            cur_other_tuple_element, ignore_metadata=ignore_metadata):
                                        # find a match, where the current tuple element is contained in one tuple
                                        # element of the other
                                        find_some_match_for_cur_self_tuple_element = True
                                        break
                                if not find_some_match_for_cur_self_tuple_element:
                                    tuple_is_complete_contained_in = False
                                    break
                            if tuple_is_complete_contained_in:
                                # find a complete valid match
                                return True
                        elif isinstance(cur_single_self.based_on_elements[0], Connection) and \
                                isinstance(cur_single_other.based_on_elements[0], Connection):
                            # both are connection trees -> check if the subtrees are contained in
                            if cur_single_self.based_on_elements[0].contained_in(
                                    cur_single_other.based_on_elements[0], ignore_metadata=ignore_metadata):
                                # find a complete valid match
                                return True
                        elif isinstance(cur_single_self.based_on_elements[0], tuple) and \
                                isinstance(cur_single_other.based_on_elements[0], Connection):
                            # this is allowed too, if every tuple item is contained_in the relevant connection
                            # check that every tuple element of self is contained in the other connection
                            for cur_self_tuple_element in cur_single_self.based_on_elements[0]:
                                if not cur_self_tuple_element.contained_in(
                                        cur_single_other, ignore_metadata=ignore_metadata):
                                    # find a match, where the current tuple element is not contained in the other
                                    # connection -> tuple can not be contained in
                                    return False
                            return True
                        # skip all others possibilities
        return False

    def intersection_with(
            self, other_conn: Union[Connection, Type[Connection],
                                    List[Connection, Type[Connection], Tuple[Connection]]]) \
            -> Union[Connection, None]:
        """
        This method returns a list of sub trees that describe the intersection of this connection sub-tree and the
        given ones. Note that this method converts all connections in **single** **resolved** connections first.
        For these connections the method checks if there are common intersections between the elements of this object
        and the given connection elements.
        The method cleans up this list and only return unique sub-connection trees!

        :param other_conn: the other sub connection tree list

        :return: the intersection connection or none, if the method has no intersection
        """
        if isinstance(other_conn, type):
            if not issubclass(other_conn, Connection):
                raise TypeError("the given `other_conn` has to be from type `Connection`")
            other_conn = other_conn()

        if isinstance(other_conn, Connection):
            if other_conn.__class__ == Connection:
                if len(other_conn.based_on_elements) == 0:
                    return self.clone()
                other_conn = other_conn.based_on_elements
            else:
                other_conn = [other_conn]

        if self.__class__ == Connection and len(self.based_on_elements) == 0:
            return Connection.based_on(*other_conn).clone()

        # determine all single connection of the two sides (could contain tuple, where every element is a single
        # connection too)
        self_conn_singles = []
        other_conn_singles = []

        idx = 0
        for cur_self_elem in self.get_singles():
            if isinstance(cur_self_elem, Connection):
                self_conn_singles.append(cur_self_elem)
            elif isinstance(cur_self_elem, type) and issubclass(cur_self_elem, Connection):
                self_conn_singles.append(cur_self_elem())
            else:
                raise TypeError(f"the element at index {idx} of `self_conn` is not from type `Connection` or is a "
                                f"tuple of that")

        idx = 0
        for cur_other_elem in other_conn:
            if isinstance(cur_other_elem, tuple):
                other_conn_singles += Connection.convert_tuple_to_singles(cur_other_elem)
            elif isinstance(cur_other_elem, Connection):
                other_conn_singles += cur_other_elem.get_singles()
            elif isinstance(cur_other_elem, type) and issubclass(cur_other_elem, Connection):
                other_conn_singles.append(cur_other_elem())
            else:
                raise TypeError(f"the element at index {idx} of `other_conn` is not from type `Connection` or is a "
                                f"tuple of that")
            idx += 1

        intersections = []
        # determine intersections between all of these single components
        for cur_self_conn in self_conn_singles:
            for cur_other_conn in other_conn_singles:
                for cur_intersection in cur_self_conn._get_intersection_with_other_single(cur_other_conn):
                    if isinstance(cur_intersection, tuple):
                        cur_intersection = Connection.based_on(cur_intersection)
                    if cur_intersection not in intersections:
                        intersections.append(cur_intersection)

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
        if len(intersection_filtered) > 1 or isinstance(intersection_filtered[0], tuple):
            return Connection.based_on(*intersection_filtered).clone()
        else:
            return intersection_filtered[0].clone()

    def append_to_based_on(self, *args: Union[Tuple[Union[Type[Connection], Connection]]]) -> None:
        """
        with this method you can extend the internal based_on list with the transferred elements. Any number of
        :meth:`Connection` objects or tuples with :meth:`Connection` objects can be given to this method

        :param args: all connection items that should be added here
        """

        for cur_idx in range(len(args)):
            cur_connection = args[cur_idx]
            if isinstance(cur_connection, type):
                if not issubclass(cur_connection, Connection):
                    raise TypeError(
                        "illegal type `{}` for parameter number {}".format(cur_connection.__name__, cur_idx))
                if self.__class__ != Connection:
                    if not cur_connection.is_parent_of(self.__class__):
                        raise IllegalConnectionTypeError(
                            "the given connection `{}` (parameter pos {}) is no parent class of the `{}`".format(
                                cur_connection.__name__, cur_idx, self.__class__.__name__))
                # this is a simple Connection type object -> simply add an instance of it to the full list
                new_conn = cur_connection()
                self._based_on_connections.append(new_conn)

            elif isinstance(cur_connection, Connection):
                if cur_connection.__class__ == Connection:
                    raise ValueError(f"it is not allowed to provide a container Connection object in based_on items - "
                                     f"found at index {cur_idx}")
                # `based_on` call for this sub-connection because we get an `Connection` object
                if self.__class__ != Connection:
                    if not cur_connection.__class__.is_parent_of(self.__class__):
                        raise IllegalConnectionTypeError(
                            "the given connection `{}` (parameter pos {}) is no parent class of the `{}`".format(
                                cur_connection.__class__.__name__, cur_idx, self.__class__.__name__))
                self._based_on_connections.append(cur_connection)

            elif isinstance(cur_connection, tuple):
                result_tuple = ()
                for cur_tuple_idx in range(len(cur_connection)):
                    cur_tuple_elem = cur_connection[cur_tuple_idx]
                    if isinstance(cur_tuple_elem, type):
                        if not issubclass(cur_tuple_elem, Connection):
                            raise TypeError(
                                "illegal type `{}` for tuple element {} for parameter number {}".format(
                                    cur_tuple_elem.__name__, cur_tuple_idx, cur_idx))
                        if self.__class__ != Connection:
                            if not cur_tuple_elem.is_parent_of(self.__class__):
                                raise IllegalConnectionTypeError(
                                    "the given connection `{}` (tuple element {} for parameter at pos {}) is no parent "
                                    "class of the `{}`".format(
                                        cur_tuple_elem.__name__, cur_tuple_idx, cur_idx, self.__class__.__name__))
                        # this is a simple Connection type object -> simply add the instance of connection to result
                        # tuple
                        result_tuple += (cur_tuple_elem(), )
                    elif isinstance(cur_tuple_elem, Connection):
                        # `based_on` call for this sub-connection because we get an `Connection` object
                        if self.__class__ != Connection:
                            if not cur_tuple_elem.__class__.is_parent_of(self.__class__):
                                raise IllegalConnectionTypeError(
                                    f"the given connection `{cur_tuple_elem.__class__.__name__}` (tuple element "
                                    f"{cur_tuple_idx} for parameter at pos {cur_idx}) is no parent class of the "
                                    f"`{self.__class__.__name__}`")
                        result_tuple += (cur_tuple_elem, )
                    elif isinstance(cur_tuple_elem, tuple):
                        raise TypeError(f"nested tuples (tuple element {cur_tuple_idx} for parameter at pos {cur_idx}) "
                                        f"and thus nested AND operations are not possible")
                    elif isinstance(cur_tuple_elem, list):
                        raise TypeError(f"nested lists (tuple element {cur_tuple_idx} for parameter at pos {cur_idx}) "
                                        f"and thus nested OR/AND operations are not possible")
                    else:
                        raise TypeError(f"illegal type `{cur_tuple_elem.__name__}` for tuple element {cur_tuple_idx} "
                                        f"for parameter at pos {cur_idx}")
                self._based_on_connections.append(result_tuple)
            else:
                raise TypeError(f"illegal type `{cur_connection.__name__}` for parameter at pos {cur_idx}")
