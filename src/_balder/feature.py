from __future__ import annotations
from typing import Type, Dict, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.device import Device
    from _balder.vdevice import VDevice

from _balder.controllers import FeatureController

from .exceptions import UnclearMethodVariationError


class Feature:
    """
    This is the basic feature class. It represents an abstract class that should not be used directly. It is the base
    class for all feature elements.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: contains a dictionary that references all vDevices of the feature and a real
                        scenario :meth:`Device` as value
        """
        from _balder.device import Device
        from _balder.vdevice import VDevice

        #: this property contains the active mapping for the devices
        self.active_vdevices: Dict[VDevice, Union[Device, str]] = {}
        all_vdevices = FeatureController.get_for(self.__class__).get_abs_inner_vdevice_classes()
        not_processed_kwargs = {}
        for cur_kwargs_key, cur_kwargs_val in kwargs.items():
            if cur_kwargs_key in [cur_vdevice.__name__ for cur_vdevice in all_vdevices]:
                cur_vdevice = [cur_vdevice for cur_vdevice in all_vdevices if cur_vdevice.__name__ == cur_kwargs_key][0]
                if isinstance(cur_kwargs_val, str) or issubclass(cur_kwargs_val, Device):
                    if not isinstance(cur_kwargs_val, str) and issubclass(cur_kwargs_val, VDevice):
                        raise TypeError(f"the given value of vDevice mapping for vDevice `{cur_kwargs_key}` has to be "
                                        f"of the type `Device` - it is a subclass of `VDevice` - this is not allowed "
                                        f"here")
                    elif self.active_vdevices != {}:
                        raise AttributeError(
                            "the constructor expects exactly none or one vDevice mapping - found more than one here")
                    else:
                        self.active_vdevices = {cur_vdevice: cur_kwargs_val}
                else:
                    raise TypeError(f"the given value of vDevice mapping for vDevice `{cur_kwargs_key}` has to be of "
                                    f"the type `Device` or has to be a string with the name of the device class")
            else:
                not_processed_kwargs[cur_kwargs_key] = cur_kwargs_val
        if len(not_processed_kwargs) != 0:
            raise TypeError(
                f"can not resolve the given attributes `{str(not_processed_kwargs)}` in feature "
                f"`{self.__class__.__name__}`")

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def active_vdevice_device_mapping(self) -> Tuple[Union[None, Type[VDevice]], Union[None, Type[Device]]]:
        """This property returns the mapped device that is active here"""
        if len(self.active_vdevices) == 0:
            return None, None
        return list(self.active_vdevices.keys())[0], list(self.active_vdevices.values())[0]

    @property
    def active_vdevice(self) -> Union[None, Type[VDevice]]:
        """This property returns the active VDevice that is active here"""
        return self.active_vdevice_device_mapping[0]

    @property
    def active_mapped_device(self) -> Union[None, Type[VDevice]]:
        """This property returns the active mapped Device"""
        return self.active_vdevice_device_mapping[1]

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def _get_inherited_method_variation(self, parent_class: Type[Feature], method_var_name: str):
        """
        This method will determine the correct inherited method-variation for the current object. For this, it searches
        in the base classes of the given `parent_class` (which has to be a parent class of `self`) for the
        method-variation that should be called.
        It automatically detects if the parent class has a method-variation or is a single normal method. In case that
        the method is a single normal method, it will directly return it, otherwise it searches the correct
        method-variation according to the vDevice mapping of the current object and return the current active
        method-variation.

        .. note::
            If this method finds the method names in more than one possible parents, it will throw an exception.

        :param parent_class: the parent class of this object, the method should start searching for the
                             `method_var_name` method (it searches in this class and all parents)

        :param method_var_name: the name of the method or of the method variation that should be returned
        """
        parent_class_controller = FeatureController.get_for(parent_class)
        if parent_class_controller.get_method_based_for_vdevice() is not None and \
                method_var_name in parent_class_controller.get_method_based_for_vdevice().keys():
            # the parent class has a method-variation -> get the current active version of it

            # first get the active data for the instantiated feature object
            active_vdevice, active_cnn_intersection, _ = self._active_method_variations[method_var_name]
            # get the vDevice object that is used in the given parent class
            if hasattr(parent_class, active_vdevice.__name__):
                parent_vdevice = getattr(parent_class, active_vdevice.__name__)
            else:
                return None

            # then determine the correct method variation according to the data of the instantiated object
            cur_method_variation = parent_class_controller.get_method_variation(
                of_method_name=method_var_name, for_vdevice=parent_vdevice,
                with_connection=active_cnn_intersection, ignore_no_findings=True)
            return cur_method_variation
        elif hasattr(parent_class, method_var_name):
            # we found one normal method in this object
            return getattr(parent_class, method_var_name)
        else:
            # execute this method for all based and check if there is exactly one
            parent_of_parent_methods = {}
            for cur_base in parent_class.__bases__:
                meth = self._get_inherited_method_variation(cur_base, method_var_name)
                if meth is not None:
                    parent_of_parent_methods[cur_base] = meth
            if len(parent_of_parent_methods) > 1:
                raise UnclearMethodVariationError(
                    f"found multiple parent classes of `{parent_class.__name__}`, that provides a method with the "
                    f"name `{method_var_name}` (base classes "
                    f"`{'`, `'.join([cur_parent.__name__ for cur_parent in parent_of_parent_methods.keys()])}`) - "
                    f"please note, that we do not support multiple inheritance")
            elif len(parent_of_parent_methods) == 1:
                return list(parent_of_parent_methods.values())[0]
            else:
                # do not found one of the methods
                return None
