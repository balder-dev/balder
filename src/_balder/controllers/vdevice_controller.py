from __future__ import annotations
from typing import Type, Dict, Union

import logging
import inspect
from _balder.vdevice import VDevice
from _balder.feature import Feature
from _balder.controllers.base_device_controller import BaseDeviceController
from _balder.exceptions import DeviceScopeError, VDeviceResolvingError

logger = logging.getLogger(__file__)


class VDeviceController(BaseDeviceController):
    """
    This is the controller class for :class:`VDevice` items.
    """
    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing VDevices and its corresponding controller object
    _items: Dict[Type[VDevice], VDeviceController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):
        super().__init__()

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != VDeviceController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`VDeviceController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, VDevice):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{VDevice.__name__}`')
        if related_cls == VDevice:
            raise TypeError(f'the attribute `related_cls` is `{VDevice.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[VDevice]) -> VDeviceController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if VDeviceController._items.get(related_cls) is None:
            item = VDeviceController(related_cls, _priv_instantiate_key=VDeviceController.__priv_instantiate_key)
            VDeviceController._items[related_cls] = item

        return VDeviceController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[VDevice]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_outer_class(self) -> Union[Type[Feature], None]:
        """
        This method delivers the outer class of this device. In Balder, this has to be a :class:`Feature`.
        """

        if self.related_cls.__qualname__.count('.') == 0:
            raise DeviceScopeError("the current device class is no inner class")
        all_splits = self.related_cls.__qualname__.split('.')

        outer_class = [cur_class for cur_name, cur_class in inspect.getmembers(
            inspect.getmodule(self.related_cls), inspect.isclass) if cur_name == all_splits[0]][0]
        # only get the next outer class (not higher)
        for cur_class_name in all_splits[1:-1]:
            outer_class = getattr(outer_class, cur_class_name)
        # instantiate it to get the real type (not the decorator class of `@for_vdevice`)
        #  we can instantiate it, because we do nothing in it
        outer_class = outer_class().__class__

        all_inner_classes = [cur_inner_class for _, cur_inner_class in inspect.getmembers(outer_class, inspect.isclass)]
        if self.related_cls in all_inner_classes:
            if not issubclass(outer_class, Feature):
                raise TypeError(f"the found outer class is of type `{outer_class.__name__}` - this is a type which is "
                                f"not allowed (outer class has to be a `Feature` class)")
            return outer_class
        raise RuntimeError(f"can not find the outer class of this vDevice `{self.related_cls.__qualname__}`")

    def get_next_parent_vdevice(self) -> Union[Type[VDevice], None]:
        """
        This method returns the next parent VDevice class, which is still a subclass of :class:`VDevice`. If the next
        parent class is :class:`VDevice`, None will be returned.

        :return: the parent VDevice class or None if no parent exists
        """
        possible_vdevices_of_interest = []
        for cur_vdevice_of_interest in self.related_cls.__bases__:
            if issubclass(cur_vdevice_of_interest, VDevice) and cur_vdevice_of_interest != VDevice:
                possible_vdevices_of_interest.append(cur_vdevice_of_interest)

        if len(possible_vdevices_of_interest) > 1:
            raise VDeviceResolvingError(
                f"the vdevice `{self.related_cls.__name__}` has more than one parent classes from type "
                f"`VDevice` - this is not allowed")

        if len(possible_vdevices_of_interest) == 1:
            # we have found one parent vDevice that has the same name as the cur_vdevice
            return possible_vdevices_of_interest[0]

        # we have no parent vDevice -> there are no parent ConnectionTree
        return None
