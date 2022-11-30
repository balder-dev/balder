from __future__ import annotations
from typing import Type, Union

import inspect
from _balder.scenario import Scenario
from _balder.utils import get_class_that_defines_method


def covered_by(item: Union[Type[Scenario], callable, None]):
    """
    This decorator defines that there exists another Scenario class or test method item that has a similar
    implementation like the decorated :class:`Scenario` class or the decorated test method.

    :param item: the element which contains the whole implementation of this scenario or test method
    """

    if item is None:
        pass
    elif callable(item) and inspect.isfunction(item) and item.__name__.startswith("test_") and \
            issubclass(get_class_that_defines_method(item), Scenario):
        pass
    elif isinstance(item, type) and issubclass(item, Scenario):
        pass
    else:
        raise TypeError("the given element for `item` must be a `Scenario` (or a subclass thereof) or a test method of "
                        "a scenario class (has to start with `test_`)")

    class CoveredByDecorator:
        def __init__(self, func):
            self.func = func

            if inspect.isclass(func):
                # it must be a class decorator
                if not issubclass(func, Scenario):
                    raise TypeError(f"The decorator `@covered_by` may only be used for `Scenario` objects or for test "
                                    f"methods of one `Scenario` object. This is not possible for the applied class "
                                    f"`{func.__name__}`.")
                if not hasattr(func, '_covered_by'):
                    func._covered_by = {}
                if func not in func._covered_by.keys():
                    func._covered_by[func] = []
                if item is None:
                    # reset it
                    func._covered_by[func] = []
                elif item not in func._covered_by[func]:
                    func._covered_by[func].append(item)
            elif inspect.isfunction(func):
                # work will done in `__set_name__`
                pass
            else:
                raise TypeError(f"The use of the `@covered_by` decorator is not allowed for the `{str(func)}` element. "
                                f"You should only use this decorator for `Scenario` elements or test method elements "
                                f"of a `Scenario` object")

        def __set_name__(self, owner, name):
            if issubclass(owner, Scenario):
                if not inspect.isfunction(self.func):
                    raise TypeError("the use of the `@covered_by` decorator is only allowed for `Scenario` objects and "
                                    "test methods of `Scenario` objects")
                if not name.startswith('test_'):
                    raise TypeError(f"the use of the `@covered_by` decorator is only allowed for `Scenario` objects "
                                    f"and test methods of `Scenario` objects - the method `{owner.__name__}.{name}` "
                                    f"does not start with `test_` and is not a valid test method")

                if not hasattr(owner, '_covered_by'):
                    owner._covered_by = {}
                if self.func not in owner._covered_by.keys():
                    owner._covered_by[self.func] = []
                if item is None:
                    # reset it
                    owner._covered_by[self.func] = []
                elif item not in owner._covered_by[self.func]:
                    owner._covered_by[self.func].append(item)
            else:
                raise TypeError(f"The use of the `@covered_by` decorator is not allowed for methods of a "
                                f"`{owner.__name__}`. You should only use this decorator for `Scenario` objects or "
                                f"valid test methods of a `Scenario` object")

            setattr(owner, name, self.func)

    return CoveredByDecorator
