from __future__ import annotations
from typing import List, Type, Tuple, Union, Literal, TYPE_CHECKING

import sys
import inspect
from _balder.scenario import Scenario
from _balder.exceptions import InheritanceError

MethodLiteralType = Literal["function", "classmethod", "staticmethod", "instancemethod"]

if TYPE_CHECKING:
    from _balder.connection import Connection
    from _balder.cnnrelations.base_connection_relation import BaseConnectionRelationT


def get_scenario_inheritance_list_of(scenario: Type[Scenario]) -> List[Type[Scenario]]:
    """
    This method returns a list, beginning with the given `scenario`, of all parent classes that are from type
    :class:´Scenario`. The last element of the list is always the original :class:`Scenario` class.

    :param scenario: the scenario the method should look for in the inheritance list

    :returns: a list with all classes that are from type scenario
    """
    if scenario == Scenario:
        return [Scenario]
    base_class_of_interest = None
    for cur_parent in scenario.__bases__:
        if issubclass(cur_parent, Scenario):
            if base_class_of_interest is not None:
                raise InheritanceError("it is not allowed to have multiple parent class that inherit from the "
                                       "class `Scenario`")
            base_class_of_interest = cur_parent

    return [scenario] + get_scenario_inheritance_list_of(base_class_of_interest)


def get_class_that_defines_method(meth):
    """credits to https://stackoverflow.com/a/25959545"""
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth), meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0], None)
        if isinstance(cls, type):
            return cls
    return None  # not required since None would have been implicitly returned anyway


def cnn_type_check_and_convert(elem: Union[Connection, Type[Connection], BaseConnectionRelationT]) \
        -> Union[Connection, BaseConnectionRelationT]:
    """
    converts possible type object to instance and checks if the element is a connection type

    :param elem: the connection object to be converted/checked
    """

    from .connection import Connection  # pylint: disable=import-outside-toplevel
    from .cnnrelations.and_connection_relation import AndConnectionRelation  # pylint: disable=import-outside-toplevel
    from .cnnrelations.or_connection_relation import OrConnectionRelation  # pylint: disable=import-outside-toplevel

    if isinstance(elem, type):
        if issubclass(elem, Connection):
            return elem()
    elif isinstance(elem, (Connection, AndConnectionRelation, OrConnectionRelation)):
        # okay
        return elem
    raise TypeError(f'object needs to be a `Connection`, a connection relation or a `Type[Connection]` - no '
                    f'`{elem}`')


def inspect_method(func) -> Tuple[Union[type, None], MethodLiteralType]:
    """
    This helper function returns the related class and the type of the method (`staticmethod`, `classmethod`,
    `instancemethod` or `function`) as tuple.
    """

    def get_func_class():
        """helper method to determine the class of the `func`"""
        classes = []
        cur_frame = sys.modules[func.__module__]
        names = func.__qualname__.split('.')[:-1]
        for cur_name in names:
            cur_frame = getattr(cur_frame, cur_name)
            if isinstance(cur_frame, type):
                classes.append(cur_frame)
        return classes[-1] if classes else None

    if func.__name__ == func.__qualname__ or '.<locals>' in func.__qualname__:
        return None, 'function'
    cls = get_func_class()
    fn_type = cls.__dict__.get(func.__name__)

    if isinstance(fn_type, classmethod):
        return cls, 'classmethod'

    if isinstance(fn_type, staticmethod):
        return cls, 'staticmethod'

    if fn_type is not None and fn_type.__class__.__name__ == 'function':
        return cls, 'instancemethod'

    raise TypeError(f'unknown element type `{func}`')
