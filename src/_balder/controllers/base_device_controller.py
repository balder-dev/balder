from __future__ import annotations
from typing import Dict, Type, Union, TYPE_CHECKING

import logging
import inspect
from abc import ABC, abstractmethod
from _balder.controllers.controller import Controller
from _balder.feature import Feature

if TYPE_CHECKING:
    from _balder.scenario import Scenario
    from _balder.setup import Setup

logger = logging.getLogger(__file__)


class BaseDeviceController(Controller, ABC):
    """
    This is the abstract controller class for :class:`Device` items.
    """
    def __init__(self):

        #: contains the original instantiated objects for the related device class (will be automatically set by
        #:  :class:`Collector`)
        self._original_instanced_features: Union[Dict[str, Feature], None] = {}

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    @abstractmethod
    def get_outer_class(self) -> Union[Type[Scenario], Type[Setup], None]:
        """
        This method delivers the outer class of this device. This has to be a :meth:`Setup` or a :meth:`Scenario`.
        """

    def get_all_instantiated_feature_objects(self) -> Dict[str, Feature]:
        """
        This method returns all instantiated :meth:`Feature` classes that were defined as static attributes within the
        related device.

        :return: supplies a dictionary with the name of the attribute as key and the current feature class as value
        """

        results = {}
        for cur_attr_name, cur_elem in inspect.getmembers(self.related_cls, lambda elem: isinstance(elem, Feature)):
            results[cur_attr_name] = cur_elem
        return results

    def get_original_instanced_feature_objects(self) -> Dict[str, Feature]:
        """
        This method returns the original instanced feature objects of the related device
        """
        return self._original_instanced_features

    def set_original_instanced_feature_objects(self, data: Union[Dict[str, Feature], None]):
        """
        This method sets the original instantiated feature object in the related device.

        :param data: the features that should be added (dictionary with the attribute name as key and
                     the instantiated feature object as value)
        """
        if data is None:
            self._original_instanced_features = None
        else:
            self._original_instanced_features = data

    def save_all_original_instanced_features(self):
        """
        This property sets the internal dictionary about the original instantiated features of this
        :class:`Device`/:class:`VDevice`. This is done, to ensure that balder has saved an original copy of the original
        instantiated abstract features. The real features will be overwritten for each new variation by the
        :class:`ExecutorTree`!
        """
        new_originals = self.get_all_instantiated_feature_objects()

        if self.get_original_instanced_feature_objects():
            if self.get_original_instanced_feature_objects() != new_originals:
                # todo we should use a balder exception here!!
                raise EnvironmentError(
                    f"the `{self.__class__.__name__}` for the item `{self.related_cls.__name__}` already has a static "
                    f"attribute value for its original instanced feature objects - can not overwrite it again")

        self.set_original_instanced_feature_objects(new_originals)
