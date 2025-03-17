from __future__ import annotations
from typing import List, Union, Type, Dict, TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod
from _balder.utils.functions import cnn_type_check_and_convert

if TYPE_CHECKING:
    from ..connection import Connection
    from ..connection import ConnectionMetadata
    from ..device import Device
    from .and_connection_relation import AndConnectionRelation
    from .or_connection_relation import OrConnectionRelation

BaseConnectionRelationT = TypeVar('BaseConnectionRelationT', bound='BaseConnectionRelation')


class BaseConnectionRelation(ABC):
    """
    This is the base connection list class, which provides the general functionality of connection collections.
    """

    def __init__(self, *connections: Union[Type[Connection], Connection, BaseConnectionRelationT]):
        self._connections = []
        # add it over append for type checking
        for connection in connections:
            self.append(connection)

    def __iter__(self):
        return self._connections.__iter__()

    def __getitem__(self, item):
        return self._connections.__getitem__(item)

    def __len__(self):
        return len(self._connections)

    def __hash__(self):
        all_hashes = 0
        for cur_elem in self.connections:
            all_hashes += hash(cur_elem) + hash(self.__class__.__name__)
        return all_hashes

    def __and__(
            self,
            other: Union[Connection, Type[Connection], AndConnectionRelation, OrConnectionRelation]
    ) -> AndConnectionRelation:

        from .and_connection_relation import AndConnectionRelation  # pylint: disable=import-outside-toplevel

        new_list = AndConnectionRelation()
        new_list.append(self)
        new_list.append(cnn_type_check_and_convert(other))
        return new_list

    def __or__(
            self,
            other: Union[Connection, Type[Connection], AndConnectionRelation, OrConnectionRelation]
    ) -> OrConnectionRelation:

        from .or_connection_relation import OrConnectionRelation  # pylint: disable=import-outside-toplevel

        new_list = OrConnectionRelation()
        new_list.append(self)
        new_list.append(cnn_type_check_and_convert(other))
        return new_list

    @property
    def connections(self) -> List[Union[Connection, BaseConnectionRelationT]]:
        """
        returns the components of this connection relation
        """
        return self._connections.copy()

    @property
    def metadata(self) -> ConnectionMetadata | None:
        """
        returns the metadata of this connection relation
        """
        if not self.connections:
            return None

        # get all unique metadata objects
        existing_metadata = list({elem.metadata for elem in self.connections if elem})
        if len(existing_metadata) > 1:
            raise ValueError(f'different metadata detected: `{existing_metadata}`')
        return existing_metadata[0]

    @abstractmethod
    def get_simplified_relation(self) -> OrConnectionRelation:
        """
        This method simplifies the connection relation. It will convert every possible relation into an
        OrConnectionRelation[Connection, AndConnectionRelation].
        """

    def clone(self):
        """
        clones this connection relation
        """
        return self.__class__(*[cnn.clone() for cnn in self._connections])

    def append(self, connection: Union[Type[Connection], Connection, BaseConnectionRelationT]):
        """
        appends a component to this connection relation
        """
        from ..connection import Connection  # pylint: disable=import-outside-toplevel

        if isinstance(connection, type):
            if issubclass(connection, Connection):
                connection = connection()
            else:
                raise TypeError(f'can not append a element `{connection.__name__}`')
        if not isinstance(connection, Connection) and not isinstance(connection, BaseConnectionRelation):
            raise TypeError('the element that should be appended to the relation needs to be a Connection or another '
                            'relation')
        if isinstance(connection, self.__class__):
            # directly add children (because it has the same type)
            for cur_inner_connection in connection.connections:
                self._connections.append(cur_inner_connection)
        else:
            self._connections.append(connection)

    def extend(self, relation: BaseConnectionRelationT):
        """
        extends the relation with the elements of provided relation
        """
        if not isinstance(relation, self.__class__):
            raise TypeError(f'the relation with the elements that should be appended needs to be from same type (is '
                            f'`{relation.__class__}` | expected `{self.__class__}`)')
        for cur_elem in relation.connections:
            self.append(cur_elem)

    def set_metadata_for_all_subitems(self, metadata: Union[Dict[str, Union[Device, str]], None]):
        """
        This method sets the metadata for all existing Connection items in this element.

        :param metadata: the metadata that should be set (if the value is explicitly set to None, it removes the
                         metadata from every item)
        """
        for cur_cnn in self._connections:
            cur_cnn.set_metadata_for_all_subitems(metadata)

    def get_all_used_connection_types(self) -> List[Type[Connection]]:
        """
        This method returns all available connection types, that are used within this connection relation.
        """
        from ..connection import Connection  # pylint: disable=import-outside-toplevel

        result = []
        for cur_inner_elem in self._connections:
            if isinstance(cur_inner_elem, Connection):
                result.append(cur_inner_elem.__class__)
            elif isinstance(cur_inner_elem, BaseConnectionRelation):
                result.extend(cur_inner_elem.get_all_used_connection_types())
            else:
                raise TypeError(f'unexpected type for inner item `{cur_inner_elem.__class__.__name__}`')
        return list(set(result))

    @abstractmethod
    def get_tree_str(self) -> str:
        """
        returns the tree string for this part of the connection tree
        """

    def is_resolved(self) -> bool:
        """
        returns whether this connection relation is part of a single connection
        """
        if len(self._connections) == 0:
            return True
        return min(cnn.is_resolved() for cnn in self._connections)

    def get_resolved(self) -> BaseConnectionRelationT:
        """
        This method returns a resolved Connection Tree. This means that it convert the based_on references so that
        every based on connection is a direct parent of the current element. It secures that there are no undefined
        connection layers between an object and the given parent.
        """
        return self.__class__(*[cnn.get_resolved() for cnn in self._connections])

    @abstractmethod
    def is_single(self) -> bool:
        """
        returns whether this connection relation is part of a single connection
        """

    @abstractmethod
    def get_singles(self) -> List[Connection]:
        """
        returns the single connections of all components of this connection relation
        """

    def cnn_are_in_other(self, other: BaseConnectionRelationT, ignore_metadata: bool=False) -> bool:
        """
        This method validates that the elements from this relation are contained in the other relation. Elements matches
        with each other, as soon as they are equal.

        .. note::
            This method only checks that every single connections from the first element is contained in the second too.
            It does not check the other direction. If you want to validate this, you need to call this method with both
            possibilities.

        :param other: the first list of connections
        :param other: the other relation object
        :param ignore_metadata: True, if the metadata of the single connections should be ignored
        :return: True in case that every connection of the first list is equal with one in the second list, otherwise
                 False
        """
        for cur_cnn in self._connections:
            found_equal = False
            for cur_other_cnn in other.connections:
                if cur_cnn.equal_with(cur_other_cnn, ignore_metadata=ignore_metadata):
                    found_equal = True
                    break
            if not found_equal:
                return False
        return True

    @abstractmethod
    def cut_into_all_possible_subtree_branches(self):
        """
        This method returns a list of all possible connection tree branches. A branch is a single connection, while
        this method returns a list of all possible singles where every single connection has this connection as head.
        """

    def equal_with(self, other_relation: BaseConnectionRelationT, ignore_metadata=False) -> bool:
        """
        This method returns True if the current relation matches with the other relation object. It always converts the
        elements to a resolved version and checks if both of them are exactly the same.

        .. note::
            Note that both connection relations need to be resolved.

        .. note::
            Note that both Connection objects have to have the same ending parent elements. Only the order of the inner
            connection elements are irrelevant.

        :param other_relation: the other connection relation (needs to be the same type)

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: returns True if both elements are same
        """
        if self.__class__ != other_relation.__class__:
            return False

        if not self.is_resolved():
            raise ValueError('can not execute method, because connection relation is not resolved')
        if not other_relation.is_resolved():
            raise ValueError('can not execute method, because other connection relation is not resolved')

        # check inner connection elements (if they match all in both directions)
        return (self.cnn_are_in_other(other_relation, ignore_metadata=ignore_metadata)
                and other_relation.cnn_are_in_other(self, ignore_metadata=ignore_metadata))

    @abstractmethod
    def contained_in(self, other_conn: Union[Connection, BaseConnectionRelationT], ignore_metadata=False) -> bool:
        """
        This method helps to find out whether this connection relation fits within a given connection tree. A connection
        object is a certain part of the large connection tree that Balder has at its disposal. This method checks
        whether a possibility of this connection tree fits in one possibility of the given connection tree.

        .. note::
            The method returns true if one single connection of this object fits in another single connection that is
            given by `other_conn`.

        :param other_conn: the other connection

        :param ignore_metadata: if this value is true the method ignores the metadata

        :return: true if the self object is contained in the `other_conn`, otherwise false
        """
