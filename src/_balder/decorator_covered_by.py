from __future__ import annotations
from typing import Type, Union

import inspect

from _balder.controllers import ScenarioController
from _balder.scenario import Scenario


def covered_by(item: Union[Type[Scenario], str, callable, None]):
    """
    This decorator defines that there exists another Scenario class or test method item that has a similar
    implementation like the decorated :class:`Scenario` class or the decorated test method.

    :param item: the element which contains the whole implementation of this scenario or test method
    """

    if item is None:
        pass
    elif isinstance(item, str) and item.startswith("test_"):
        pass
    elif callable(item) and inspect.isfunction(item) and item.__name__.startswith("test_"):
        pass
    elif isinstance(item, type) and issubclass(item, Scenario):
        raise NotImplementedError('The covered-by other scenario classes is not supported yet')
    else:
        raise TypeError("the given element for `item` must be a test method of a scenario class (has to start with "
                        "`test_`)")

    class CoveredByDecorator:
        """decorator class for `@covered_by` decorator"""
        def __init__(self, func):
            self.func = func

            if inspect.isclass(func):
                # it must be a class decorator
                if not issubclass(func, Scenario):
                    raise TypeError(f"The decorator `@covered_by` may only be used for `Scenario` objects or for test "
                                    f"methods of one `Scenario` object. This is not possible for the applied class "
                                    f"`{func.__name__}`.")
                raise NotImplementedError('The covered-by decoration of other scenario classes is not supported yet')
                # scenario_controller = ScenarioController.get_for(func)
                # register for the whole class
                # scenario_controller.register_covered_by_for(meth=None, covered_by=item)
            if inspect.isfunction(func):
                # work will done in `__set_name__`
                pass
            else:
                raise TypeError(f"The use of the `@covered_by` decorator is not allowed for the `{str(func)}` element. "
                                f"You should only use this decorator for test method elements of a `Scenario` object")

        def __set_name__(self, owner, name):
            if issubclass(owner, Scenario):
                if not inspect.isfunction(self.func):
                    raise TypeError("the use of the `@covered_by` decorator is only allowed for test methods of "
                                    "`Scenario` objects")
                if not name.startswith('test_'):
                    raise TypeError(f"the use of the `@covered_by` decorator is only allowed for test methods of "
                                    f"`Scenario` objects - the method `{owner.__name__}.{name}` does not start with "
                                    f"`test_` and is not a valid test method")
                # if item is a string - resolve method
                cleared_item = item
                if isinstance(item, str):
                    cleared_item = getattr(owner, item)
                scenario_controller = ScenarioController.get_for(owner)
                scenario_controller.register_covered_by_for(meth=name, covered_by=cleared_item)
            else:
                raise TypeError(f"The use of the `@covered_by` decorator is not allowed for methods of a "
                                f"`{owner.__name__}`. You should only use this decorator for valid test methods of a "
                                f"`Scenario` object")

            setattr(owner, name, self.func)

    return CoveredByDecorator
