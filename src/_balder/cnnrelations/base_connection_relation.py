from __future__ import annotations
from typing import List, Union, Type, Dict, TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod
from ..utils import cnn_type_check_and_convert

if TYPE_CHECKING:
    from ..connection import Connection
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
