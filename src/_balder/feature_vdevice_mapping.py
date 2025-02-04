from __future__ import annotations
from typing import Type
import dataclasses

from .controllers.feature_controller import FeatureController
from .device import Device
from .feature import Feature
from .vdevice import VDevice


class FeatureVDeviceMapping:
    """
    helper object that stores mappings between :class:`VDevice` and :class:`Device`
    """

    @dataclasses.dataclass
    class VDeviceDeviceMapping:
        """describes the mapping of one VDevice to one Device"""
        #: the vdevice class
        vdevice: Type[VDevice]
        #: the mapped device to this VDevice
        device: Type[Device]

    @dataclasses.dataclass
    class VDevicesMapping:
        """
        stores a single mapping
        """
        #: the feature object, this mapping belongs to
        feature: Feature
        #: the available mapping for this feature (at the moment, we only support one)
        mappings: list[FeatureVDeviceMapping.VDeviceDeviceMapping]

    def __init__(self):
        self._mappings: list[FeatureVDeviceMapping.VDevicesMapping] = []

    @property
    def mappings(self) -> list[VDevicesMapping]:
        """
        returns all existing mappings
        """
        return list(self._mappings)

    @property
    def features(self) -> list[Feature]:
        """
        returns all used attribute names
        """
        return [mapping.feature for mapping in self._mappings]

    def items(self) -> list[tuple[Feature, list[VDeviceDeviceMapping]]]:
        """
        :return: a list of Feature/vdevice mapping tuples
        """
        return [(mapping.feature, mapping.mappings) for mapping in self._mappings]

    def add(self, feature: Feature, mappings: dict[Type[VDevice], Type[Device]]):
        """
        adds a new mapping

        :param feature: the :class:`Feature` class this mapping belongs to
        :param mappings: a dictionary that describes the mapping between the :class:`VDevice` and :class:`Device`. The
                         :class:`VDevice` needs to be part of the :class:`Feature`
        """
        if feature in self.features:
            raise KeyError(f'entry for feature `{feature}` already exist - can not define it multiple times')
        feature_controller = FeatureController.get_for(feature.__class__)
        vdevice_device_mappings = []
        for cur_vdev, cur_dev in mappings.items():
            if not (isinstance(cur_vdev, type) and issubclass(cur_vdev, VDevice)):
                raise TypeError(f'the provided key objects in mappings needs to be a subclass of `{VDevice.__name__}`')
            if not (isinstance(cur_dev, type) and issubclass(cur_dev, Device)):
                raise TypeError(f'the provided value objects in mappings needs to be a subclass of `{Device.__name__}`')
            if cur_vdev not in feature_controller.get_abs_inner_vdevice_classes():
                raise ValueError(f'the provided VDevice `{cur_vdev}` is not part of the provided feature `{feature}`')
            vdevice_device_mappings.append(self.VDeviceDeviceMapping(cur_vdev, cur_dev))
        new_mapping = self.VDevicesMapping(feature=feature, mappings=vdevice_device_mappings)

        self._mappings.append(new_mapping)

    def get_mappings_for_feature(self, feature: Feature) -> list[VDeviceDeviceMapping]:
        """
        returns the list with all mappings for the provided feature
        """
        for cur_item in self._mappings:
            if cur_item.feature == feature:
                return cur_item.mappings
        raise KeyError(f'entry for feature `{feature}` does not exist')
