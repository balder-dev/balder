from __future__ import annotations

import logging
from abc import ABC
from typing import Dict, List, Type, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.scenario import Scenario
    from _balder.setup import Setup
    from _balder.connection import Connection
    from _balder.device import Device
    from _balder.vdevice import VDevice
    from _balder.controllers import ScenarioController, SetupController

import inspect
from .base_device_controller import BaseDeviceController
from _balder.exceptions import DeviceScopeError

logger = logging.getLogger(__file__)


class DeviceController(BaseDeviceController, ABC):
    """
    This is the main device controller to manage :class:`Device` classes.
    """
    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing setup devices and its corresponding controller object
    _items: Dict[Type[Device], DeviceController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):
        super(DeviceController, self).__init__()
        from _balder.device import Device
        from _balder.vdevice import VDevice

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != DeviceController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`DeviceController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Device):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Device.__name__}` but not of '
                            f'`{VDevice.__name__}`')
        if issubclass(related_cls, VDevice):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Device.__name__}` but not of '
                            f'`{VDevice.__name__}`')
        if related_cls == Device:
            raise TypeError(f'the attribute `related_cls` is `{Device.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

        # internal counter to auto provide unique node names
        self._node_cnt = 0

        #: contains all raw existing connection decorators for the related device
        self._connections: Dict[str, List[Connection]] = {}

        #: describes the absolute connections from the related device to another device
        self._absolute_connections: Dict[Type[Device], List[Connection]] = {}

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Device]) -> DeviceController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if DeviceController._items.get(related_cls) is None:
            item = DeviceController(
                related_cls, _priv_instantiate_key=DeviceController.__priv_instantiate_key)
            DeviceController._items[related_cls] = item

        return DeviceController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Device]:
        """the related device type"""
        return self._related_cls

    @property
    def connections(self) -> Dict[str, List[Connection]]:
        """
        returns the defined connections for the related devices (sorted after node name) - NOT SYNCHRONIZED -
        direct decorator values
        """
        return self._connections

    @property
    def absolute_connections(self) -> Dict[Type[Device], List[Connection]]:
        """
        returns the absolute and SYNCHRONIZED connections between the related device and all other devices
        """
        return self._absolute_connections

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def __get_outer_class_controller(self) -> Union[ScenarioController, SetupController]:
        from _balder.scenario import Scenario
        from _balder.setup import Setup
        from _balder.controllers import ScenarioController, SetupController

        outer_class = self.get_outer_class()
        if issubclass(outer_class, Setup):
            outer_class_controller = SetupController.get_for(outer_class)
        elif issubclass(outer_class, Scenario):
            outer_class_controller = ScenarioController.get_for(outer_class)
        else:
            raise TypeError(f"type `{outer_class.__name__}` given from `get_outer_class()` is wrong")
        return outer_class_controller

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def add_new_raw_connection(self, connection: Connection):
        """
        This method adds a new raw connection to the internal property `connections`.

        :param connection: the connection object (the related device has to be part of it)
        """
        if connection.from_device == self.related_cls:
            own_node = connection.from_node_name
        elif connection.to_device == self.related_cls:
            own_node = connection.to_node_name
        else:
            raise ValueError("the given connection does not have the current device as component")
        if own_node not in self._connections.keys():
            self._connections[own_node] = []

        self._connections[own_node].append(connection)

    def add_new_absolute_connection(self, connection: Connection):
        """
        This method adds a new absolute connection to the internal property `absolute_connections`.

        .. note::
            This method doesn't secure any synchronizing, it only sets the connection internally.

        .. note::
            It only adds a connection, if it does not already exist in the internal list - duplicates will not be added.

        :param connection: the connection object (the related device has to be part of it)
        """
        if self.related_cls == connection.from_device:
            other_device = connection.to_device
        elif self.related_cls == connection.to_device:
            other_device = connection.from_device
        else:
            raise ValueError("the given connection does not have the current device as component")
        if other_device not in self._absolute_connections.keys():
            self._absolute_connections[other_device] = []
        if connection not in self._absolute_connections[other_device]:
            self._absolute_connections[other_device].append(connection)

    def cleanup_absolute_connections_with(self, other_device):
        """
        This method removes all connections from the related device to the given ``other_device``.
        """
        if other_device in self._absolute_connections.keys():
            del self._absolute_connections[other_device]

    def get_all_connections(self) -> Dict[str, List[Connection]]:
        """
        This method returns all available connection objects for the related device, sorted accordingly to their node
        name. The method gets all possible connection objects from the outer class (the setup or the scenario) and sorts
        the relevant ones.

        The method detects connections from other devices of the outer class that starts or ends at the related device,
        too.

        :returns: returns a mapping between the node name and a list of :class:`Connection` objects that belongs to the
                  node
        """
        outer_class_controller = self.__get_outer_class_controller()

        all_outer_class_conns = outer_class_controller.get_all_connections()
        conns_as_from_device = [
            cur_conn for cur_conn in all_outer_class_conns if cur_conn.from_device == self.related_cls]
        conns_as_to_device = [
            cur_conn for cur_conn in all_outer_class_conns if cur_conn.to_device == self.related_cls]
        result_dict = {}
        for cur_conn in conns_as_from_device:
            if cur_conn.from_node_name not in result_dict.keys():
                result_dict[cur_conn.from_node_name] = []
            result_dict[cur_conn.from_node_name].append(cur_conn)

        for cur_conn in conns_as_to_device:
            if cur_conn.to_node_name not in result_dict.keys():
                result_dict[cur_conn.to_node_name] = []
            result_dict[cur_conn.to_node_name].append(cur_conn)
        return result_dict

    def get_all_absolute_connections(self) -> Dict[str, List[Connection]]:
        """
        This method returns all available absolute connection objects for the related device, sorted accordingly to
        their node name. Absolute connection are the cleaned connections, that are reduced to work with all used
        :class:`Feature` and their :class:`VDevice` classes.

        The method also gets all possible connection objects from the outer class and sorts the relevant ones. The
        method detects connections from other devices of the outer class that starts or ends here, too.

        :returns: returns a mapping between the node name and a list of :class:`.Connection` objects that belongs to
                  the node
        """
        # we do not need to look in communication partner device here, because `_absolute_connections` is always be
        # synchronized
        outer_class_controller = self.__get_outer_class_controller()
        all_outer_class_devices = outer_class_controller.get_all_abs_inner_device_classes()

        result_dict = {}
        for cur_outer_class_device in all_outer_class_devices:
            cur_outer_class_device_controller = DeviceController.get_for(cur_outer_class_device)

            for _, cur_cnn_list in cur_outer_class_device_controller.absolute_connections.items():
                for cur_cnn in cur_cnn_list:
                    if cur_cnn.from_device == self.related_cls:
                        if cur_cnn.from_node_name not in result_dict.keys():
                            result_dict[cur_cnn.from_node_name] = []
                        if cur_cnn not in result_dict[cur_cnn.from_node_name]:
                            result_dict[cur_cnn.from_node_name].append(cur_cnn)
                    elif cur_cnn.to_device == self.related_cls:
                        if cur_cnn.to_node_name not in result_dict.keys():
                            result_dict[cur_cnn.to_node_name] = []
                        if cur_cnn not in result_dict[cur_cnn.to_node_name]:
                            result_dict[cur_cnn.to_node_name].append(cur_cnn)
        return result_dict

    # def _get_all_gateways(self) -> List[NodeGateway]:
    #     """provides a list with all gateway objects that are defined for this device"""
    #     self.__validate_gateway_node_names()
    #     return self._gateways.copy()

    # def __validate_gateway_node_names(self):
    #     """
    #     this method checks whether all `node_name` keys for the defined gateways really exist
    #     """
    #     if len(self._gateways) > 0 and self not in self._connections.keys():
    #         raise NodeNotExistsError(
    #              f"gateways are defined for non-existent nodes for the device {self.related_cls.__name__}")
    #     for cur_gateway in self._gateways:
    #         cur_gateway.validate_given_node_names()

    def get_node_types(self) -> Dict[str, List[Connection, Tuple[Connection]]]:
        """
        This method returns a dictionary with the node name as key and a connection class as value. This class
        describes the common connection sub-tree, that all incoming and outgoing connections of the related device have
        in common.

        :raises MultipleNodeBaseException: is thrown if the method finds several unrelated connections as a basis
        """

        result = {}
        all_connections = self.get_all_connections()
        for cur_node_name in all_connections.keys():
            cur_intersection = all_connections[cur_node_name][0]
            for cur_node_connection in all_connections[cur_node_name][1:]:
                cur_intersection = cur_node_connection.intersection_with(cur_intersection)
            result[cur_node_name] = [cur_intersection]

        return result

    def get_new_empty_auto_node(self) -> str:
        """
        This helper method returns a new empty node name. This method can be used if balder should manage node names
        automatically.
        """

        self_node_name = "n{}".format(self._node_cnt)
        self._node_cnt += 1
        return self_node_name

    def get_outer_class(self) -> Union[Type[Scenario], Type[Setup], None]:
        """
        This method delivers the outer class of the related device. This has to be a :class:`Setup` or a
        :class:`Scenario`.
        """
        from _balder.scenario import Scenario
        from _balder.setup import Setup

        if self.related_cls.__qualname__.count('.') == 0:
            raise DeviceScopeError("the current device class is no inner class")
        elif self.related_cls.__qualname__.count('.') > 1:
            raise DeviceScopeError("the current device class is no direct inner class (deeper than one)")

        outer_class_name, inner_class_name = self.related_cls.__qualname__.split('.')

        outer_class = [cur_class for cur_name, cur_class in inspect.getmembers(
            inspect.getmodule(self.related_cls)) if cur_name == outer_class_name][0]

        all_inner_classes = [cur_inner_class for _, cur_inner_class in inspect.getmembers(outer_class, inspect.isclass)]
        if self.related_cls in all_inner_classes:
            if not issubclass(outer_class, Setup) and not issubclass(outer_class, Scenario):
                raise TypeError(
                    f"the outer class is of the type `{outer_class.__name__}` - this is not allowed")
            return outer_class
        raise RuntimeError(f"can not find the outer class of this given device `{self.related_cls.__qualname__}`")
