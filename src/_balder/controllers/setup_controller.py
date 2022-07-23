from __future__ import annotations

import logging
from typing import Type, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.setup import Setup

from .normal_scenario_setup_controller import NormalScenarioSetupController

logger = logging.getLogger(__file__)


class SetupController(NormalScenarioSetupController):
    """
    This is the controller class for :class:`Setup` items.
    """

    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing setups and its corresponding controller object
    _items: Dict[Type[Setup], SetupController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):
        from _balder.setup import Setup

        # describes if the current controller is for setups or for scenarios (has to be set in child controller)
        self._related_type = Setup

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != SetupController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`SetupController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Setup):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Setup.__name__}`')
        if related_cls == Setup:
            raise TypeError(f'the attribute `related_cls` is `{Setup.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Setup]) -> SetupController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if SetupController._items.get(related_cls) is None:
            item = SetupController(related_cls, _priv_instantiate_key=SetupController.__priv_instantiate_key)
            SetupController._items[related_cls] = item

        return SetupController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Setup]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------
