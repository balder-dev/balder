from __future__ import annotations

import logging
from abc import ABC
from typing import Type, List, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.device import Device
    from _balder.connection import Connection
    from _balder.controllers import ScenarioController
    from _balder.controllers import SetupController

import inspect
from _balder.setup import Setup
from _balder.scenario import Scenario
from _balder.controllers.controller import Controller
from _balder.controllers.device_controller import DeviceController
from _balder.exceptions import MultiInheritanceError, DeviceOverwritingError


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
        from _balder.controllers import ScenarioController, SetupController
        if issubclass(related_cls, Scenario):
            return ScenarioController.get_for(related_cls)
        elif issubclass(related_cls, Setup):
            return SetupController.get_for(related_cls)
        else:
            raise TypeError(f"illegal non supported type `{related_cls.__name__}` given for `related_cls`")

    def get_all_inner_device_classes(self) -> List[Type[Device]]:
        """
        This method provides a list of all :meth:`Device` classes that have been defined as inner classes in the related
        scenario or setup.
        """
        from _balder.device import Device

        all_classes = inspect.getmembers(self.related_cls, inspect.isclass)
        filtered_classes = []
        for _, cur_class in all_classes:
            if not issubclass(cur_class, Device):
                # filter all classes and make sure that only the child classes of :meth:`Device` remain
                continue
            outer_class_name, device_class_name = cur_class.__qualname__.split('.')
            if outer_class_name != self.related_cls.__name__:
                # filter all classes that do not match the setup name in __qualname__
                continue
            # otherwise, add this candidate
            filtered_classes.append(cur_class)
        return filtered_classes

    def get_all_abs_inner_device_classes(self) -> List[Type[Device]]:
        """
        This method provides a list of all :meth:`Device` classes that are valid for the related scenario or setup
        class. If the class itself does not implement some inner devices by its own, it returns the absolute inner
        devices of the next higher setup/scenario parent class.
        """
        cls_devices = self.get_all_inner_device_classes()
        if len(cls_devices) == 0:
            # search for parent class
            base_class = None
            for cur_base in self.related_cls.__bases__:
                if issubclass(cur_base, self._related_type):
                    if base_class is not None:
                        raise MultiInheritanceError(
                            f"the class `{self.related_cls.__name__}` has multiple parent classes from type `Scenario`")
                    base_class = cur_base
            if base_class == self._related_type:
                # if the class type is the original `Setup` or `Scenario` type -> no inner devices exists
                return []
            return self.__class__.get_for(base_class).get_all_abs_inner_device_classes()
        else:
            return cls_devices

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
            for cur_other_device, cur_connections in cur_device_controller.absolute_connections.items():
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
        parent_scenario_or_setup = None
        for cur_base_class in self.related_cls.__bases__:
            if issubclass(cur_base_class, Scenario) or issubclass(cur_base_class, Setup):
                if parent_scenario_or_setup is not None:
                    # multi inheritance is not allowed
                    raise MultiInheritanceError(
                        f"found more than one Scenario/Setup parent classes for `{self.related_cls.__name__}` "
                        f"- multi inheritance is not allowed for Scenario/Setup classes")
                parent_scenario_or_setup = cur_base_class
        if parent_scenario_or_setup == Scenario or parent_scenario_or_setup == Setup:
            # done, because the parent class is direct Scenario/Setup class
            return

        parent_scenario_or_setup_controller = self.__class__.get_for(parent_scenario_or_setup)

        devices = self.get_all_inner_device_classes()
        abs_parent_devices = parent_scenario_or_setup_controller.get_all_abs_inner_device_classes()
        abs_parent_devices_as_names = [cur_parent.__name__ for cur_parent in abs_parent_devices]

        if len(devices) == 0:
            # ignore it because cur item has no own device definitions
            return
        else:
            # check that a device is newly defined or has the same name as the parent device
            for cur_item_device in devices:
                # check if name exists in parent
                relevant_parent_according_naming = None
                if cur_item_device.__name__ in abs_parent_devices_as_names:
                    relevant_parent_according_naming = \
                        abs_parent_devices[abs_parent_devices_as_names.index(cur_item_device.__name__)]

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
                found_parent = False
                for cur_item_device in devices:
                    if issubclass(cur_item_device, cur_parent):
                        found_parent = True
                        break
                if not found_parent:
                    raise DeviceOverwritingError(
                        f"found a device `{cur_parent.__qualname__}` which is part of a parent class, but it is "
                        f"not implemented in child class `{self.related_cls.__name__}`")

        # also check the parent class here
        self.__class__.get_for(parent_scenario_or_setup).validate_inheritance()
