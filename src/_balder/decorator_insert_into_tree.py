from __future__ import annotations
from typing import Type, Union, List, Tuple

from _balder.connection import Connection


def insert_into_tree(parents: List[Union[Type[Connection], Tuple[Type[Connection]]]] = None, tree_name: str = ""):
    """
    This decorator inserts a :meth:`Connection` object into the global connection tree.

    :param parents: all items that are parents of the decorated connection

    :param tree_name: the tree name the connection should be inserted in
    """
    if parents is None:
        parents = []
    if not isinstance(parents, list):
        raise ValueError("the value of `parents` must be a `list`")

    idx = 0
    for cur_parent in parents:
        if isinstance(cur_parent, tuple):
            tuple_idx = 0
            for cur_tuple_element in cur_parent:
                if not isinstance(cur_tuple_element, type) or not issubclass(cur_tuple_element, Connection):
                    raise TypeError(
                        f"the tuple element on index {tuple_idx} (located on index {idx} of `parents`)  must be a "
                        f"`Connection` type (given element is: {str(cur_parent)})")
                tuple_idx += 1
        else:
            if not isinstance(cur_parent, type) or not issubclass(cur_parent, Connection):
                raise TypeError(
                    f"the element on index {idx} in `parents` must be a `Connection` type (given: {str(cur_parent)})")
        idx += 1

    class MyDecorator:
        """decorator class for `@insert_into_tree` decorator"""
        def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument

            nonlocal parents

            decorated_cls = args[0]

            conn_parents = decorated_cls.get_parents(tree_name=tree_name)
            conn_parents = [] if conn_parents is None else conn_parents

            conn_parents += [new_parent for new_parent in parents if new_parent not in conn_parents]
            decorated_cls.set_parents(conn_parents, tree_name=tree_name)

            return decorated_cls

    return MyDecorator
