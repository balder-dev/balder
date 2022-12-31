from __future__ import annotations
from typing import Type, Dict, List, Tuple

import logging
import inspect
from _balder.device import Device
from _balder.scenario import Scenario
from _balder.connection import Connection
from _balder.controllers.feature_controller import FeatureController
from _balder.controllers.device_controller import DeviceController
from _balder.controllers.normal_scenario_setup_controller import NormalScenarioSetupController
from _balder.exceptions import UnclearAssignableFeatureConnectionError, ConnectionIntersectionError

logger = logging.getLogger(__file__)


class ScenarioController(NormalScenarioSetupController):
    """
    This is the controller class for :class:`Scenario` items.
    """

    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing scenarios and its corresponding controller object
    _items: Dict[Type[Scenario], ScenarioController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):

        # describes if the current controller is for setups or for scenarios (has to be set in child controller)
        self._related_type = Scenario

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != ScenarioController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`ScenarioController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Scenario):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Scenario.__name__}`')
        if related_cls == Scenario:
            raise TypeError(f'the attribute `related_cls` is `{Scenario.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Scenario]) -> ScenarioController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if ScenarioController._items.get(related_cls) is None:
            item = ScenarioController(related_cls, _priv_instantiate_key=ScenarioController.__priv_instantiate_key)
            ScenarioController._items[related_cls] = item

        return ScenarioController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Scenario]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_all_test_methods(self) -> List[callable]:
        """
        This method returns all test methods that were defined in the related scenario. A testmethod has to start with
        `test_*`.
        """
        all_relevant_func = []

        all_methods = inspect.getmembers(self.related_cls, inspect.isfunction)
        for cur_method_name, cur_function in all_methods:
            if cur_method_name.startswith('test_'):
                all_relevant_func.append(cur_function)

        return all_relevant_func

    def validate_feature_clearance_for_parallel_connections(self):
        """
        This method validates for every active class-based feature (only the ones that have an active VDevice<->Device
        mapping), that there exist a clear scenario-device-connection for this feature. The method throws an
        :class:`UnclearAssignableFeatureConnectionError` if there exists more than one possible device-connection
        for the related devices and the method is not able to determine a clear connection.
        """

        for cur_from_device in self.get_all_abs_inner_device_classes():
            # determine all VDevice-Device mappings for this one, by iterating over all instantiated Feature classes
            cur_from_device_instantiated_features = \
                DeviceController.get_for(cur_from_device).get_all_instantiated_feature_objects()
            for _, cur_feature in cur_from_device_instantiated_features.items():
                mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                if mapped_device is None:
                    # ignore this, because we have no vDevices here
                    continue

                # now check if one or more single of the classbased connection are CONTAINED IN the possible
                # parallel connection (only if there exists more than one parallel)
                feature_cnn = Connection.based_on(*FeatureController.get_for(
                        cur_feature.__class__).get_class_based_for_vdevice()[mapped_vdevice])

                # search node names that is the relevant connection
                relevant_cnns: List[Connection] = []
                mapped_device_abs_cnns = DeviceController.get_for(mapped_device).get_all_absolute_connections()
                for _, all_connections in mapped_device_abs_cnns.items():
                    relevant_cnns += [cur_cnn for cur_cnn in all_connections
                                      if cur_cnn.has_connection_from_to(cur_from_device, mapped_device)]

                if len(relevant_cnns) <= 1:
                    # ignore if there are not more than one relevant connection
                    continue

                # there are some parallel connections -> check that only one fits with the feature
                matched_relevant_cnns = []
                for cur_relevant_cnn in relevant_cnns:
                    cur_relevant_cnn_singles = cur_relevant_cnn.get_singles()

                    for cur_relevant_single in cur_relevant_cnn_singles:
                        matches = [True for cur_feature_cnn in feature_cnn.get_singles()
                                   if cur_feature_cnn.contained_in(cur_relevant_single)]
                        if len(matches):
                            matched_relevant_cnns.append(True)
                            break
                if sum(matched_relevant_cnns) > 1:
                    raise UnclearAssignableFeatureConnectionError(
                        f"the devices {cur_from_device.__name__} and {mapped_device.__name__} have "
                        f"multiple parallel connections - the device `{cur_from_device.__name__}` uses a "
                        f"feature `{cur_feature.__class__.__name__}` that matches with the device "
                        f"`{mapped_device.__name__}`, but it is not clear which of the parallel connection "
                        f"could be used")

    def get_feature_cleaned_absolute_single_connections(self) -> \
            Tuple[Dict[Type[Device], Dict[str, Dict[Type[Device], Dict[str, List[Connection]]]]],  Dict[
                Tuple[Device, Device], List[Connection]]]:
        """
        This method returns all absolute-single connections between all devices of this scenario, but already cleaned
        based on the cumulated class-based decorators of all the feature devices.

        .. note::
            Please note, that the reduction candidates connections do not have to be unique.

        :return: returns a tuple with the cleaned up connections (sorted as dictionary per device) and the reduced
                 connections as second element
        """
        reduction_candidates = {}

        def add_reduction_candidate(device, other_device, connections: Connection):

            if (device, other_device) not in reduction_candidates.keys() and \
                    (other_device, device) not in reduction_candidates.keys():
                # we have to add it as new list
                reduction_candidates[(device, other_device)] = [connections]
            elif (device, other_device) in reduction_candidates.keys():
                reduction_candidates[(device, other_device)].append(connections)
            elif (other_device, device) in reduction_candidates.keys():
                reduction_candidates[(other_device, device)].append(connections)

        # start to generate the singles for every connection between the devices of every scenario
        all_abs_single_connections = self.get_absolute_single_connections()

        all_devices = self.get_all_abs_inner_device_classes()
        for cur_from_device in all_devices:
            # determine all VDevice-Device mappings for this one, by iterating over all instantiated Feature classes
            cur_from_device_instantiated_features = \
                DeviceController.get_for(cur_from_device).get_all_instantiated_feature_objects()
            for _, cur_feature in cur_from_device_instantiated_features.items():
                mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                if mapped_device is None:
                    # ignore this, because we have no vDevices here
                    continue

                # now try to reduce the scenario connections according to the requirements of the feature class
                cur_feature_class_based_for_vdevice = \
                    FeatureController.get_for(
                        cur_feature.__class__).get_class_based_for_vdevice()[mapped_vdevice]
                feature_cnn = Connection.based_on(*cur_feature_class_based_for_vdevice)
                # search node names that is the relevant connection
                relevant_cnns: List[List[Connection]] = []
                for _, cur_node_data in all_abs_single_connections[cur_from_device].items():
                    for cur_to_device, cur_to_device_data in cur_node_data.items():
                        if cur_to_device == mapped_device:
                            for _, cur_cnns in cur_to_device_data.items():
                                relevant_cnns.append(cur_cnns)
                device_cnn_singles = None
                if len(relevant_cnns) > 1:
                    # there exists parallel connections - filter only the relevant one
                    for cur_single_cnns in relevant_cnns:
                        for cur_single_cnn in cur_single_cnns:
                            if feature_cnn.contained_in(cur_single_cnn):
                                # this is the relevant connection (all other can not fit, because we have
                                # already checked this with method
                                # `scenario_controller.validate_feature_clearance_for_parallel_connections()`)
                                device_cnn_singles = cur_single_cnns
                                break
                        if device_cnn_singles is not None:
                            break
                elif len(relevant_cnns) == 1:
                    device_cnn_singles = relevant_cnns[0]
                if device_cnn_singles is None:
                    raise ValueError("can not find relevant connection of all parallel connections")

                if device_cnn_singles[0].from_device == cur_from_device:
                    device_node_name = device_cnn_singles[0].from_node_name
                    mapped_node_name = device_cnn_singles[0].to_node_name
                else:
                    device_node_name = device_cnn_singles[0].to_node_name
                    mapped_node_name = device_cnn_singles[0].from_node_name

                # execute further process only if there is exactly one relevant connection
                start_length_before_reduction = \
                    len(all_abs_single_connections[cur_from_device][device_node_name][
                            mapped_device][mapped_node_name])
                for cur_abs_connection in \
                        all_abs_single_connections[cur_from_device][device_node_name][
                            mapped_device][mapped_node_name].copy():
                    if not feature_cnn.contained_in(cur_abs_connection, ignore_metadata=True):
                        # this abs single connection is not fulfilled by the current feature -> remove it
                        all_abs_single_connections[cur_from_device][device_node_name][
                            mapped_device][mapped_node_name].remove(cur_abs_connection)
                        add_reduction_candidate(cur_from_device, mapped_device, cur_abs_connection)
                if start_length_before_reduction > 0 and \
                        len(all_abs_single_connections[cur_from_device][device_node_name][
                                mapped_device][mapped_node_name]) == 0:
                    raise ConnectionIntersectionError(
                        f"the `{self.related_cls.__name__}` has a connection from device "
                        f"`{cur_from_device.__name__}` to `{mapped_device.__name__}` - some mapped VDevices of "
                        f"their feature classes define mismatched connections")
                # do the same for the opposite direction (features are always bidirectional)
                start_length_before_reduction = \
                    len(all_abs_single_connections[mapped_device][mapped_node_name][
                            cur_from_device][device_node_name])
                for cur_abs_connection in \
                        all_abs_single_connections[mapped_device][mapped_node_name][
                            cur_from_device][device_node_name].copy():
                    if not feature_cnn.contained_in(cur_abs_connection, ignore_metadata=True):
                        # this abs single connection is not being fulfilled by the current feature -> remove it
                        all_abs_single_connections[mapped_device][mapped_node_name][
                            cur_from_device][device_node_name].remove(cur_abs_connection)
                        add_reduction_candidate(cur_from_device, mapped_device, cur_abs_connection)
                if start_length_before_reduction > 0 and \
                        len(all_abs_single_connections[mapped_device][mapped_node_name][
                                cur_from_device][device_node_name]) == 0:
                    raise ConnectionIntersectionError(
                        f"the `{self.related_cls.__name__}` has a connection from device "
                        f"`{cur_from_device.__name__}` to `{mapped_device.__name__}` - some mapped VDevices of "
                        f"their feature classes define mismatched connections")
        return all_abs_single_connections, reduction_candidates

    def determine_absolute_device_connections(self):
        """
        This method determines the real possible Sub-Connections for every element of the scenarios. For this the method
        will create a possible intersection connection, for the :class:´Connection´ between two devices and
        all :class:`Connection`-Subtrees that are allowed for the mapped vDevices in the used :class:`Feature`
        classes.
        The data will be saved in the :class:`Device` property ``_absolute_connections``. If the method detects an empty
        intersection between two devices that are connected through a VDevice-Device mapping, the method will throw an
        exception.
        """

        # start to generate the singles for every connection between the devices of every scenario
        all_abs_single_connections, reduction_candidates = self.get_feature_cleaned_absolute_single_connections()

        # generate all required warnings
        for cur_warning_tuple in reduction_candidates:
            logger.warning(f"detect some connections between the devices `{cur_warning_tuple[0].__name__}` and "
                           f"`{cur_warning_tuple[1].__name__}` of scenario `{self.related_cls.__name__}` that can be "
                           f"reduced, because their related features only use a subset of the defined connection")

        # first cleanup the relevant absolute connections
        for cur_from_device, from_device_data in all_abs_single_connections.items():
            for _, from_node_data in from_device_data.items():
                for cur_to_device, to_device_data in from_node_data.items():
                    cur_from_device_controller = DeviceController.get_for(cur_from_device)
                    cur_to_device_controller = DeviceController.get_for(cur_to_device)

                    cur_from_device_controller.cleanup_absolute_connections_with(cur_to_device)
                    cur_to_device_controller.cleanup_absolute_connections_with(cur_from_device)

        # replace all absolute connection with the single ones
        for cur_from_device, from_device_data in all_abs_single_connections.items():
            for _, from_node_data in from_device_data.items():
                for cur_to_device, to_device_data in from_node_data.items():
                    for _, cur_single_cnns in to_device_data.items():

                        cur_from_device_controller = DeviceController.get_for(cur_from_device)
                        cur_to_device_controller = DeviceController.get_for(cur_to_device)

                        new_cnn = Connection.based_on(*cur_single_cnns)
                        new_cnn.set_metadata_for_all_subitems(cur_single_cnns[0].metadata)
                        if cur_from_device == cur_single_cnns[0].from_device:
                            cur_from_device_controller.add_new_absolute_connection(new_cnn)
                        else:
                            cur_to_device_controller.add_new_absolute_connection(new_cnn)
