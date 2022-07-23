from __future__ import annotations

import logging
from abc import ABC
from typing import Type, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.device import Device
    from _balder.scenario import Scenario
    from _balder.setup import Setup
    from _balder.connection import Connection

import inspect
from .controller import Controller
from .device_controller import DeviceController
from _balder.exceptions import MultiInheritanceError


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
