from __future__ import annotations

import copy
from typing import Dict, List, Type, Union, TYPE_CHECKING

import logging
import inspect
from abc import ABC
from _balder.setup import Setup
from _balder.device import Device
from _balder.vdevice import VDevice
from _balder.scenario import Scenario
from _balder.controllers.base_device_controller import BaseDeviceController
from _balder.controllers.feature_controller import FeatureController
from _balder.exceptions import DeviceResolvingException, InnerFeatureResolvingError, \
    FeatureOverwritingError, MultiInheritanceError
if TYPE_CHECKING:
    from _balder.connection import Connection
    from _balder.controllers import ScenarioController, SetupController
    from _balder.node_gateway import NodeGateway

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
        super().__init__()

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

        self._gateways: List[NodeGateway] = []

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
        # pylint: disable-next=import-outside-toplevel
        from _balder.controllers.normal_scenario_setup_controller import NormalScenarioSetupController

        outer_class = self.get_outer_class()
        return NormalScenarioSetupController.get_for(outer_class)

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_next_parent_class(self) -> Union[Type[Device], None]:
        """
        This method returns the next parent class which is a subclass of the :class:`Device` itself.

        :return: returns the next parent class or None if the next parent class is :class:`Device`
                 itself
        """
        next_base_class = None
        for cur_base in self.related_cls.__bases__:
            if issubclass(cur_base, Device):
                if next_base_class is not None:
                    raise MultiInheritanceError(
                        f"found more than one Device parent classes for `{self.related_cls.__name__}` "
                        f"- multi inheritance is not allowed for Device classes")
                next_base_class = cur_base
        if next_base_class == Device:
            return None
        return next_base_class

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

    def add_new_raw_gateway(self, gateway: NodeGateway):
        """
        This method adds a new raw gateway to the internal property `_gateways`.

        :param gateway: the gateway object (the related device has to be part of it)
        """
        if gateway.device != self.related_cls:
            raise ValueError("the given gateway does not have the current device as component")

        self._gateways.append(gateway)

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

    def get_node_types(self) -> Dict[str, List[Connection | None]]:
        """
        This method returns a dictionary with the node name as key and a connection class as value. This class
        describes the common connection sub-tree, that all incoming and outgoing connections of the related device have
        in common.

        :raises MultipleNodeBaseException: is thrown if the method finds several unrelated connections as a basis
        """

        result = {}
        all_connections = self.get_all_connections()
        for cur_node_name, node_connections in all_connections.items():
            cur_intersection = node_connections[0]
            for cur_node_connection in node_connections[1:]:
                cur_intersection = cur_node_connection.intersection_with(cur_intersection)
            result[cur_node_name] = [cur_intersection]

        return result

    def get_new_empty_auto_node(self) -> str:
        """
        This helper method returns a new empty node name. This method can be used if balder should manage node names
        automatically.
        """

        self_node_name = f"n{self._node_cnt}"
        self._node_cnt += 1
        return self_node_name

    def get_outer_class(self) -> Union[Type[Scenario], Type[Setup], None]:
        """
        This method delivers the outer class of the related device. This has to be a :class:`Setup` or a
        :class:`Scenario`.
        """
        return getattr(self.related_cls, '_outer_balder_class', None)

    def resolve_connection_device_strings(self):
        """
        This method ensures that device names, that are provided as strings within connections between the current
        device and another device (which is given as string), are resolved. Since the `@connect` marker makes it
        possible to specify the other device as a string, this method will exchange these strings with the related
        device class.

        .. note::
            This is required, because in some cases you have to provide the devices for the decorator as a string,
            because the outer class could be imported later than the execution of the decorator was done. After Balder
            has read all files, all required information are available and this method should be able to resolve the
            device-strings.
        """
        for _, node_connections in self.connections.items():
            for cur_conn in node_connections:
                # for every connection applies that the `from_device` must already be a type; also the
                # `to_device` has to be an inner class of this type

                if isinstance(cur_conn.to_device, type) and issubclass(cur_conn.to_device, Device):
                    # Skip because resolving already done
                    return

                # get outer class of `from_device`
                from_device_controller = DeviceController.get_for(cur_conn.from_device)
                parent_cls_from_device = from_device_controller.get_outer_class()

                all_inner_classes_of_outer = dict(inspect.getmembers(parent_cls_from_device, inspect.isclass))
                if cur_conn.to_device in all_inner_classes_of_outer.keys():
                    meta = cur_conn.metadata

                    to_device = all_inner_classes_of_outer[cur_conn.to_device]
                    # if there was given no unique node -> create one
                    to_device_node_name = DeviceController.get_for(to_device).get_new_empty_auto_node() \
                        if meta.to_node_name is None else meta.to_node_name

                    meta.set_to(
                        to_device=to_device,
                        to_device_node_name=to_device_node_name)

                    cur_conn.set_metadata_for_all_subitems(meta)
                else:
                    raise DeviceResolvingException(
                        f"cannot resolve the str for the given device class `{cur_conn.to_device}` for "
                        f"`@connect` decorator at device `{cur_conn.from_device.__qualname__}`")

    def validate_inner_referenced_features(self):
        """
        This method validates that every :class:`Feature` that is referenced from another :class:`Feature` of this
        device also exists in the definition list of this device.
        """
        all_instantiated_feature_objs = self.get_all_instantiated_feature_objects()
        for _, cur_feature in all_instantiated_feature_objs.items():
            cur_feature_controller = FeatureController.get_for(cur_feature.__class__)
            # now check the inner referenced features of this feature and check if that exists in the device
            for cur_ref_feature_name, cur_ref_feature in \
                    cur_feature_controller.get_inner_referenced_features().items():
                potential_candidates = []
                for _, cur_potential_candidate_feature in all_instantiated_feature_objs.items():
                    if isinstance(cur_potential_candidate_feature, cur_ref_feature.__class__):
                        # the current match is the current feature itself -> not allowed to reference itself
                        if cur_potential_candidate_feature == cur_feature:
                            raise InnerFeatureResolvingError(
                                f"can not reference the same feature from itself (done in feature "
                                f"`{cur_feature.__class__.__name__}` with `{cur_ref_feature_name}`)")
                        potential_candidates.append(cur_potential_candidate_feature)

                if len(potential_candidates) == 0:
                    raise InnerFeatureResolvingError(
                        f"can not find a matching feature in the device `{self.related_cls.__name__}` that could "
                        f"be assigned to the inner feature reference `{cur_ref_feature_name}` of the feature "
                        f"`{cur_feature.__class__.__name__}`")

                if len(potential_candidates) > 1:
                    raise InnerFeatureResolvingError(
                        f"found more than one matching feature in the device `{self.related_cls.__name__}` that "
                        f"could be assigned to the inner feature reference `{cur_ref_feature_name}` of the "
                        f"feature `{cur_feature.__class__.__name__}`")

    def validate_inheritance_of_instantiated_features(self):
        """
        This method validates instantiated features and check that they are inherited correctly. It checks that the
        feature of a child device is also a child class of the feature of the parent device (in case they use the same
        property name).
        """

        all_instantiated_feature_objs = self.get_all_instantiated_feature_objects()
        # only one match possible, because we already have checked it before
        next_base_device = self.get_next_parent_class()
        if next_base_device is not None:
            next_base_device_controller = DeviceController.get_for(next_base_device)
            # also execute this method for the base device
            next_base_device_controller.validate_inheritance_of_instantiated_features()
            all_parent_instantiated_feature_objs = next_base_device_controller.get_all_instantiated_feature_objects()
        else:
            all_parent_instantiated_feature_objs = {}

        for cur_attr_name, cur_feature in all_instantiated_feature_objs.items():
            if cur_attr_name in all_parent_instantiated_feature_objs.keys():
                # attribute name also exists before -> check if the feature is a parent of the current one
                if not isinstance(cur_feature, all_parent_instantiated_feature_objs[cur_attr_name].__class__):
                    raise FeatureOverwritingError(
                        f"the feature `{cur_feature.__class__.__name__}` with the attribute name `{cur_attr_name}` "
                        f"of the device `{self.related_cls.__name__}` you are trying to overwrite is no child class of "
                        f"the feature `{all_parent_instantiated_feature_objs[cur_attr_name].__class__.__name__}` "
                        f"that was assigned to this property before")

    def resolve_mapped_vdevice_strings(self):
        """
        This method updates the inner VDevice-Device mappings for every instantiated :class:`.Feature`, if the
        mapped device (value in constructor) was given as a string. It secures that this device has a real
        :class:`VDevice` reference for its mapped VDevice.
        """
        all_instanced_features = self.get_original_instanced_feature_objects()
        scenario_or_setup_controller = self.__get_outer_class_controller()
        if all_instanced_features is None:
            # has no features -> skip
            return
        for cur_attr_name, cur_feature in all_instanced_features.items():
            # clone feature and its active_device dict to make sure that shared instances in parent classes are handled
            # correctly
            new_feature = copy.copy(cur_feature)
            new_feature.active_vdevices = {**cur_feature.active_vdevices}
            setattr(self.related_cls, cur_attr_name, new_feature)
            if new_feature.active_vdevices != {}:
                # do something only if there exists an internal mapping
                for cur_mapped_vdevice, cur_mapped_device in new_feature.active_vdevices.items():
                    if isinstance(cur_mapped_device, str):
                        resolved_device = \
                            scenario_or_setup_controller.get_inner_device_class_by_string(cur_mapped_device)
                        if resolved_device is None:
                            raise RuntimeError(
                                f"found no possible matching name while trying to resolve "
                                f"the given vDevice string `{cur_mapped_vdevice}` in feature "
                                f"`{new_feature.__class__.__name__}`")
                        new_feature.active_vdevices[cur_mapped_vdevice] = resolved_device
