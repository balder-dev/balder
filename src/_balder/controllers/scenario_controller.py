from __future__ import annotations
from typing import Type, Dict, List

import logging
import inspect
from _balder.scenario import Scenario
from _balder.connection import Connection
from _balder.controllers.feature_controller import FeatureController
from _balder.controllers.device_controller import DeviceController
from _balder.controllers.normal_scenario_setup_controller import NormalScenarioSetupController
from _balder.exceptions import UnclearAssignableFeatureConnectionError

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

                # now check if one or more single of the classbased connection are CONTAINED IN the possible
                # parallel connection (only if there exists more than one parallel)
                cur_feature_class_based = \
                    FeatureController.get_for(
                        cur_feature.__class__).get_class_based_for_vdevice()[mapped_vdevice]
                feature_cnn = Connection.based_on(*cur_feature_class_based)
                feature_cnns_singles = feature_cnn.get_singles()

                # search node names that is the relevant connection
                relevant_cnns: List[Connection] = []
                mapped_device_abs_cnns = DeviceController.get_for(mapped_device).get_all_absolute_connections()
                for _, all_connections in mapped_device_abs_cnns.items():
                    for cur_cnn in all_connections:
                        if cur_cnn.has_connection_from_to(cur_from_device, mapped_device):
                            relevant_cnns.append(cur_cnn)

                if len(relevant_cnns) > 1:
                    # there are some parallel connections -> check that only one fits with the feature
                    matched_relevant_cnns = []
                    for cur_relevant_cnn in relevant_cnns:
                        cur_relevant_cnn_singles = cur_relevant_cnn.get_singles()
                        matched = False
                        for cur_relevant_single in cur_relevant_cnn_singles:
                            for cur_feature_cnn in feature_cnns_singles:
                                if cur_feature_cnn.contained_in(cur_relevant_single):
                                    matched = True
                                    break
                            if matched:
                                matched_relevant_cnns.append(True)
                                break
                    if sum(matched_relevant_cnns) > 1:
                        raise UnclearAssignableFeatureConnectionError(
                            f"the devices {cur_from_device.__name__} and {mapped_device.__name__} have "
                            f"multiple parallel connections - the device `{cur_from_device.__name__}` uses a "
                            f"feature `{cur_feature.__class__.__name__}` that matches with the device "
                            f"`{mapped_device.__name__}`, but it is not clear which of the parallel connection "
                            f"could be used")
