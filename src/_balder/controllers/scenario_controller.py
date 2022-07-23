from __future__ import annotations

import logging
import inspect
from typing import Type, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.scenario import Scenario

from .normal_scenario_setup_controller import NormalScenarioSetupController


logger = logging.getLogger(__file__)


class ScenarioController(NormalScenarioSetupController):
    """
    This is the controller class for :class:`Scenario` items.
    """

    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing scenarios and its corresponding controller object
    _items: Dict[Type[Scenario], ScenarioController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):
        from _balder.scenario import Scenario

        # describes if the current controller is for setups or for scenarios (has to be set in child controller)
        self._related_type = Scenario

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != ScenarioController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`ScenarioController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Scenario):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Scenario.__name__}`')
        if related_cls == Scenario:
            raise TypeError(f'the attribute `related_cls` is `{Scenario.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Scenario]) -> ScenarioController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if ScenarioController._items.get(related_cls) is None:
            item = ScenarioController(related_cls, _priv_instantiate_key=ScenarioController.__priv_instantiate_key)
            ScenarioController._items[related_cls] = item

        return ScenarioController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Scenario]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_all_test_methods(self) -> List[callable]:
        """
        This method returns all test methods that were defined in the related scenario. A testmethod has to start with
        `test_*`.
        """
        all_relevant_func = []

        all_methods = inspect.getmembers(self.related_cls, inspect.isfunction)
        for cur_method_name, cur_function in all_methods:
            if cur_method_name.startswith('test_'):
                all_relevant_func.append(cur_function)

        return all_relevant_func
