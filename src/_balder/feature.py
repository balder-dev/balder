from __future__ import annotations
from typing import Type, Dict, Tuple, Union

from _balder.device import Device
from _balder.vdevice import VDevice
from _balder.utils.inner_device_managing_metaclass import InnerDeviceManagingMetaclass


class Feature(metaclass=InnerDeviceManagingMetaclass):
    """
    This is the basic feature class. It represents an abstract class that should not be used directly. It is the base
    class for all feature elements.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: contains a dictionary that references all vDevices of the feature and a real
                        scenario :meth:`Device` as value
        """
        from _balder.controllers import FeatureController  # pylint: disable=import-outside-toplevel

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
                    if self.active_vdevices:
                        raise AttributeError(
                            "the constructor expects exactly none or one vDevice mapping - found more than one here")

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
