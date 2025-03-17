from __future__ import annotations
from typing import Type, List, Union, Optional, Dict, TYPE_CHECKING

import logging
import inspect
from abc import ABC, abstractmethod
from _balder.setup import Setup
from _balder.device import Device
from _balder.scenario import Scenario
from _balder.connection_metadata import ConnectionMetadata
from _balder.controllers.controller import Controller
from _balder.controllers.device_controller import DeviceController
from _balder.controllers.vdevice_controller import VDeviceController
from _balder.exceptions import MultiInheritanceError, DeviceOverwritingError, MissingFeaturesOfVDeviceError

if TYPE_CHECKING:
    from _balder.connection import Connection
    from _balder.controllers import ScenarioController
    from _balder.controllers import SetupController

logger = logging.getLogger(__file__)


class NormalScenarioSetupController(Controller, ABC):
    """
    This is the abstract base controller class for the Scenario- and Setup-Controller.
    """
    # describes if the current controller is for setups or for scenarios (has to be set in child controller)
    _related_type: Optional[Type[Scenario, Setup]] = None

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    @staticmethod
    def get_for(related_cls) -> Union[ScenarioController, SetupController]:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.

        .. note::
            This method automatically returns the correct controller type, depending on the class you provide with
            `related_cls`.
        """
        # pylint: disable-next=import-outside-toplevel
        from _balder.controllers.setup_controller import SetupController
        # pylint: disable-next=import-outside-toplevel
        from _balder.controllers.scenario_controller import ScenarioController

        if issubclass(related_cls, Scenario):
            return ScenarioController.get_for(related_cls)
        if issubclass(related_cls, Setup):
            return SetupController.get_for(related_cls)

        raise TypeError(f"illegal non supported type `{related_cls.__name__}` given for `related_cls`")

    def get_all_inner_device_classes(self) -> List[Type[Device]]:
        """
        This method provides a list of all :meth:`Device` classes that have been defined as inner classes in the related
        scenario or setup.
        """

        all_classes = inspect.getmembers(self.related_cls, inspect.isclass)
        filtered_classes = []
        for _, cur_class in all_classes:
            if not issubclass(cur_class, Device):
                # filter all classes and make sure that only the child classes of :meth:`Device` remain
                continue
            if DeviceController.get_for(cur_class).get_outer_class() != self.related_cls:
                # filter all classes that do not match the setup name in __qualname__
                continue
            # otherwise, add this candidate
            filtered_classes.append(cur_class)
        return filtered_classes

    def get_inner_device_class_by_string(self, device_str: str) -> Union[Type[Device], None]:
        """
        This method returns the inner Device class for the given string.

        :param device_str: the name string of the Device that should be returned

        :return: the Device class or None, if the method has not found any class with this name
        """
        possible_devs = [cur_vdevice for cur_vdevice in self.get_all_inner_device_classes()
                         if cur_vdevice.__name__ == device_str]
        if len(possible_devs) == 0:
            return None
        if len(possible_devs) > 1:
            raise RuntimeError("found more than one possible vDevices - something unexpected happened")

        return possible_devs[0]

    def get_all_abs_inner_device_classes(self) -> List[Type[Device]]:
        """
        This method provides a list of all :meth:`Device` classes that are valid for the related scenario or setup
        class. If the class itself does not implement some inner devices by its own, it returns the absolute inner
        devices of the next higher setup/scenario parent class.
        """
        cls_devices = self.get_all_inner_device_classes()
        if len(cls_devices) == 0:
            # search for parent class
            base_class = self.get_next_parent_class()

            if base_class is None:
                # if the class type is the original `Setup` or `Scenario` type -> no inner devices exists
                return []
            return self.__class__.get_for(base_class).get_all_abs_inner_device_classes()

        return cls_devices

    def get_abs_inner_device_class_by_string(self, device_str: str) -> Union[Type[Device], None]:
        """
        This method returns the absolute inner Device class for the given string.

        :param device_str: the name string of the Device that should be returned

        :return: the Device class or None, if the method has not found any class with this name
        """
        possible_devs = [cur_vdevice for cur_vdevice in self.get_all_abs_inner_device_classes()
                         if cur_vdevice.__name__ == device_str]
        if len(possible_devs) == 0:
            return None
        if len(possible_devs) > 1:
            raise RuntimeError("found more than one possible vDevices - something unexpected happened")

        return possible_devs[0]

    @abstractmethod
    def get_next_parent_class(self) -> Union[Type[Scenario], Type[Setup], None]:
        """
        This method returns the next parent class which is a subclass of the :class:`Scenario`/:class:`Setup` itself.

        :return: returns the next parent class or None if the next parent class is :class:`Scenario`/:class:`Setup`
                 itself
        """

    def get_all_connections(self) -> List[Connection]:
        """
        This method returns all connection objects which have been defined between devices of the related class.
        """
        all_device_classes = self.get_all_inner_device_classes()
        all_connections = []
        for cur_device in all_device_classes:
            cur_device_controller = DeviceController.get_for(cur_device)
            for cur_node_name in cur_device_controller.connections.keys():
                all_connections += cur_device_controller.connections[cur_node_name]
        return all_connections

    def get_all_abs_connections(self) -> List[Connection]:
        """
        This method returns all absolute connection objects which have been defined between absolute devices of the
        related scenario or setup class.
        """
        all_device_classes = self.get_all_abs_inner_device_classes()
        all_connections = []
        for cur_device in all_device_classes:
            cur_device_controller = DeviceController.get_for(cur_device)
            for _, cur_connections in cur_device_controller.absolute_connections.items():
                for cur_cnn in cur_connections:
                    if cur_cnn not in all_connections:
                        all_connections.append(cur_cnn)
        return all_connections

    def validate_inheritance(self):
        """
        This method validates that the inheritance of the related :class:`Setup`/:class:`Scenario` class was done
        correctly. It checks that all inner devices that are inherited has the same naming as their parents and also
        that every reused name (that is already be used for a device in the parent class) does also inherit from this
        parent scenario/setup device.

        In addition to that, it secures that either all devices are overwritten in the current class or no devices are
        overwritten in the related class.
        """

        # get parent scenario / setup class and check no multi inheritance
        parent_scenario_or_setup = self.get_next_parent_class()
        if parent_scenario_or_setup is None:
            # done, because the parent class is direct Scenario/Setup class
            return

        parent_scenario_or_setup_controller = self.__class__.get_for(parent_scenario_or_setup)

        devices = self.get_all_inner_device_classes()
        abs_parent_devices = parent_scenario_or_setup_controller.get_all_abs_inner_device_classes()
        abs_parent_devices_by_name = {cur_parent.__name__: cur_parent for cur_parent in abs_parent_devices}

        if len(devices) == 0:
            # ignore it because cur item has no own device definitions
            return

        # check that a device is newly defined or has the same name as the parent device
        for cur_item_device in devices:
            # check if name exists in parent
            relevant_parent_according_naming = abs_parent_devices_by_name.get(cur_item_device.__name__, None)

            # check if device is inherited from a parent
            relevant_parent_device_according_inheritance = None
            for cur_parent in abs_parent_devices:
                if issubclass(cur_item_device, cur_parent):
                    if relevant_parent_device_according_inheritance is not None:
                        # multi inheritance is not allowed
                        raise MultiInheritanceError(
                            f"found more than one {self._related_type.__name__}-Device parent classes for the "
                            f"class `{cur_item_device.__name__}` - multi inheritance is not allowed for device "
                            f"classes")
                    relevant_parent_device_according_inheritance = cur_parent

            # now check if both is fulfilled
            if relevant_parent_according_naming == relevant_parent_device_according_inheritance and \
                    relevant_parent_device_according_inheritance is not None:
                # device is inherited AND has the same name as used in parent -> ALLOWED
                pass
            elif relevant_parent_according_naming is None and relevant_parent_device_according_inheritance is None:
                # both are none -> it is a new device -> ALLOWED
                pass
            elif relevant_parent_according_naming is None:
                # reused a naming but does not inherit from it -> NOT ALLOWED
                raise DeviceOverwritingError(
                    f"the inner device class `{cur_item_device.__qualname__}` which inherits from another "
                    f"device `{relevant_parent_device_according_inheritance.__qualname__}` - it should also have "
                    f"the same name")
            elif relevant_parent_device_according_inheritance is None:
                # inherit from a parent device, but it doesn't have the same naming -> NOT ALLOWED
                raise DeviceOverwritingError(
                    f"the inner device class `{cur_item_device.__qualname__}` has the same name than the "
                    f"device `{relevant_parent_according_naming.__qualname__}` - it should also inherit from it")

        # secure that all parent devices are implemented here too
        for cur_parent in abs_parent_devices:
            found_parent = len([dev for dev in devices if issubclass(dev, cur_parent)]) > 0
            if not found_parent:
                raise DeviceOverwritingError(
                    f"found a device `{cur_parent.__qualname__}` which is part of a parent class, but it is "
                    f"not implemented in child class `{self.related_cls.__name__}`")

        # also check the parent class here
        self.__class__.get_for(parent_scenario_or_setup).validate_inheritance()

    def check_vdevice_feature_existence(self):
        """
        This method validates that the :class:`Feature` property set of a :class:`Device` holds all required
        :class:`Feature` objects of the related :class:`VDevice`. For this the method checks that every feature (that
        is used in a mapped :class:`VDevice`) also exists as a child :class:`Feature` property in the related
        :class:`Device` class.

        .. note::
            Variations are not related to this and will not be checked here.

        """

        for cur_device in self.get_all_abs_inner_device_classes():
            cur_device_instantiated_features = \
                DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
            for _, cur_feature in cur_device_instantiated_features.items():
                active_vdevice, related_device = cur_feature.active_vdevice_device_mapping
                if active_vdevice is None:
                    # ignore this, because no active vdevice exists
                    continue

                # secure that all the defined features in the VDevice also exist in the related device ->
                #  otherwise error
                orig_device_features = [
                    feat for _, feat in
                    DeviceController.get_for(related_device).get_all_instantiated_feature_objects().items()]
                active_vdevice_instantiated_features = \
                    VDeviceController.get_for(active_vdevice).get_all_instantiated_feature_objects()
                for _, cur_vdevice_feature in active_vdevice_instantiated_features.items():
                    # search for it
                    found_it = False
                    for cur_orig_feature in orig_device_features:
                        if isinstance(cur_orig_feature, cur_vdevice_feature.__class__):
                            found_it = True
                            break
                    if not found_it:
                        raise MissingFeaturesOfVDeviceError(
                            f"the device `{related_device.__name__}` which is mapped to the VDevice "
                            f"`{active_vdevice.__name__}` doesn't have an implementation for the feature "
                            f"`{cur_vdevice_feature.__class__.__name__}` required by the VDevice class "
                            f"`{active_vdevice.__name__}`")

    def get_absolute_single_connections(self) -> \
            Dict[Type[Device], Dict[str, Dict[Type[Device], Dict[str, List[Connection]]]]]:
        """
        This method determines the synchronized (both devices of a connection were updated) absolute connections
        between all devices of this scenario/setup.

        :return: returns a dictionary which provides all single connections between two devices that can be accessed
                 with `result[dev1][node-of-dev1][dev2][node-of-dev2]`
        """
        # start to generate the singles for every connection between the devices of every scenario
        all_abs_single_connections = {}

        all_devices = self.get_all_abs_inner_device_classes()
        for cur_from_device in all_devices:
            cur_from_device_controller = DeviceController.get_for(cur_from_device)

            # generate the whole `all_abs_single_connections` and convert the connections to singles
            for cur_to_device, cur_connections in cur_from_device_controller.absolute_connections.items():
                for cur_cnn in cur_connections:
                    if cur_from_device == cur_cnn.from_device:
                        cur_from_node = cur_cnn.from_node_name
                        cur_to_node = cur_cnn.to_node_name
                    else:
                        cur_from_node = cur_cnn.to_node_name
                        cur_to_node = cur_cnn.from_node_name
                    if cur_from_device not in all_abs_single_connections.keys():
                        all_abs_single_connections[cur_from_device] = {}
                    if cur_from_node not in all_abs_single_connections[cur_from_device].keys():
                        all_abs_single_connections[cur_from_device][cur_from_node] = {}
                    if cur_to_device not in \
                            all_abs_single_connections[cur_from_device][cur_from_node].keys():
                        all_abs_single_connections[cur_from_device][
                            cur_from_node][cur_to_device] = {}
                    if cur_to_node not in \
                            all_abs_single_connections[cur_from_device][cur_from_node][cur_to_device].keys():
                        all_abs_single_connections[cur_from_device][cur_from_node][cur_to_device][
                            cur_to_node] = cur_cnn.get_singles()
                        # we do not have to set the connection in communication device, because the absolute
                        # connections are always synchronized
                    else:
                        raise ValueError(
                            f'found multiple definitions for connection from device '
                            f'{cur_from_device.__qualname__} (node: `{cur_from_node}`) to device '
                            f'{cur_to_device.__qualname__} (node: `{cur_to_node}`) in scenario '
                            f'`{self.related_cls.__name__}`')
        return all_abs_single_connections

    def determine_raw_absolute_device_connections(self):
        """
        This method determines and creates the basic `_absolute_connections` for the related scenario/setup. Note,
        that this method only creates the class attribute and adds the synchronized connections (same on both sides if
        they are bidirectional). It does not analyse or take :class:`Feature` classes into consideration.
        """
        # determine next relevant base class
        next_base_class = self.get_next_parent_class()

        # executed this method for all parents too
        if next_base_class:
            NormalScenarioSetupController.get_for(next_base_class).determine_raw_absolute_device_connections()

        all_relevant_cnns = []

        all_devices = self.get_all_inner_device_classes()
        all_devices_as_strings = [search_device.__name__ for search_device in all_devices]

        # check if the devices of the current item has minimum one own connect() decorator
        has_connect_decorator = False
        for cur_device in all_devices:
            if len(DeviceController.get_for(cur_device).connections) > 0:
                has_connect_decorator = True

        if len(all_devices) == 0 and len(self.get_all_abs_inner_device_classes()) > 0:
            # only the parent class has defined scenarios -> use absolute data from next parent
            #  NOTHING TO DO, because we also use these devices in child setup/scenario
            return

        if len(all_devices) > 0 and not has_connect_decorator:
            # the current item has defined devices, but no own `@connect()` decorator -> use absolute data from
            #  next parent
            if next_base_class is not None:
                # only if there is a next base class
                next_base_class_controller = NormalScenarioSetupController.get_for(next_base_class)

                for cur_parent_cnn in next_base_class_controller.get_all_abs_connections():

                    # find all related devices (for this connection)
                    related_from_device = \
                        all_devices[all_devices_as_strings.index(cur_parent_cnn.from_device.__name__)]
                    related_to_device = all_devices[all_devices_as_strings.index(cur_parent_cnn.to_device.__name__)]
                    new_cnn = cur_parent_cnn.clone()
                    new_cnn.set_metadata_for_all_subitems(ConnectionMetadata(
                        from_device=related_from_device, from_device_node_name=cur_parent_cnn.from_node_name,
                        to_device=related_to_device, to_device_node_name=cur_parent_cnn.to_node_name)
                    )
                    all_relevant_cnns.append(new_cnn)

                # throw warning (but only if this scenario/setup has minimum one of the parent classes has inner
                # devices (and connection between them) by its own)
                if len(next_base_class_controller.get_all_abs_inner_device_classes()) > 0 and \
                        len(next_base_class_controller.get_all_abs_connections()) > 0:
                    logger.warning(
                        f"the collected `{self.related_cls.__name__}` class overwrites devices, but does "
                        f"not define connections between them by its own - please provide them in case you "
                        f"overwrite devices")
        else:
            # otherwise, use data from current layer, because there is no parent, no devices or this item overwrites
            # the connections from higher classes
            for cur_device in all_devices:
                for _, cur_cnn_list in DeviceController.get_for(cur_device).connections.items():
                    # now add every single connection correctly into the dictionary
                    all_relevant_cnns += [cur_cnn for cur_cnn in cur_cnn_list if cur_cnn not in all_relevant_cnns]

        # now set the absolute connections correctly
        for cur_cnn in all_relevant_cnns:
            DeviceController.get_for(cur_cnn.from_device).add_new_absolute_connection(cur_cnn)
            DeviceController.get_for(cur_cnn.to_device).add_new_absolute_connection(cur_cnn)
