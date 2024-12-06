from __future__ import annotations
from typing import List, Union, Type, TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod
from ..utils import cnn_type_check_and_convert

if TYPE_CHECKING:
    from ..connection import Connection
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

    @abstractmethod
    def get_tree_str(self) -> str:
        """
        returns the tree string for this part of the connection tree
        """
