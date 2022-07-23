from __future__ import annotations

import logging
from typing import Type, Union, List, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.feature import Feature
    from _balder.scenario import Scenario
    from _balder.vdevice import VDevice
    from _balder.executor.scenario_executor import ScenarioExecutor
    from _balder.fixture_manager import FixtureManager

import sys
import inspect
import traceback
from _balder.device import Device
from _balder.connection import Connection
from _balder.testresult import ResultState, BranchBodyResult
from _balder.executor.basic_executor import BasicExecutor
from _balder.executor.testcase_executor import TestcaseExecutor
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.routing_path import RoutingPath
from _balder.controllers import DeviceController, VDeviceController, FeatureController
from _balder.exceptions import NotApplicableVariationError, UnclearAssignableFeatureConnectionError

logger = logging.getLogger(__file__)


class VariationExecutor(BasicExecutor):
    """
    A VariationExecutor only contains :meth:`TestcaseExecutor` children.
    """

    def __init__(self, device_mapping: Dict[Type[Device], Type[Device]], parent: ScenarioExecutor):
        super(VariationExecutor, self).__init__()
        self._testcase_executors = []
        self._base_device_mapping = device_mapping
        self._parent_executor = parent
        self._fixture_manager = parent.fixture_manager

        # contains the active routings for the current variation
        self._routings: Dict[Connection, List[RoutingPath]] = {}
        # buffer variable to save the feature replacement after it was determined with
        # `determine_feature_replacement_and_vdevice_mappings()`
        self._feature_replacement: \
            Union[None, Dict[Type[Device], Dict[str, Tuple[Union[Feature, None], Feature]]]] = None
        # buffer variable to save the feature replacement after it was determined with
        # `determine_feature_replacement_and_vdevice_mappings()`
        self._abs_setup_feature_vdevice_mappings: \
            Union[None, Dict[Type[Device], Dict[Feature, Dict[Type[VDevice], Type[Device]]]]] = None

        # contains the absolute scenario device connections for the current variation
        self._abs_variation_scenario_device_connections: Union[List[Connection], None] = None
        # contains the absolute active variation connections (intersection between scenario based
        # `_abs_variation_scenario_device_connections` and virtual connection from active RoutingPath objects from
        # `_routings`)
        self._abs_variation_connections: Union[List[Connection], None] = None

        # contains the original active vdevice mappings for all scenario and setup devices (will be managed by
        # `update_active_vdevice_device_mappings_in_scenario_and_setup_devices()` and
        # `revert_active_vdevice_device_mappings_in_scenario_and_setup_devices()`)
        self._original_active_vdevice_mappings: \
            Dict[Type[Device], Dict[Feature, Dict[Type[VDevice], Type[Device]]]] = {}

        # contains the result object for the BODY part of this branch
        self.body_result = BranchBodyResult(self)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def base_instance(self) -> object:
        """
        returns the base class instance to which this executor instance belongs to
        """
        return None

    @property
    def parent_executor(self) -> ScenarioExecutor:
        return self._parent_executor

    @property
    def cur_scenario_class(self) -> Scenario:
        """property returns the current :class:`Scenario` for this variation"""
        return self._parent_executor.base_scenario_class

    @property
    def cur_setup_class(self) -> Setup:
        """property returns the current :class:`Setup` for this variation"""
        return self._parent_executor._parent_executor.base_setup_class

    @property
    def base_device_mapping(self) -> Dict[Type[Device], Type[Device]]:
        """
        property returns the device mapping which is a dictionary with the scenario devices as keys and their related
        setup devices as values
        """
        return self._base_device_mapping

    @property
    def all_child_executors(self) -> List[TestcaseExecutor]:
        return self.testcase_executors

    @property
    def testcase_executors(self) -> List[TestcaseExecutor]:
        return self._testcase_executors

    @property
    def fixture_manager(self) -> FixtureManager:
        return self._fixture_manager

    @property
    def feature_replacement(self) -> Dict[Type[Device], Dict[str, Tuple[Union[Feature, None], Feature]]]:
        """
        this property is a dictionary with every scenario device as key and a dictionary as value - the value dictionary
        contains a tuple (inner dict value) for every attribute name(inner dict key) - the tuples always consist of two
        elements, the old feature as first item of the tuple (the instantiated feature from the scenario if it exists,
        otherwise this is None) and the new feature as second item (the feature of the related Setup-Device)
        """
        return self._feature_replacement

    @property
    def abs_setup_feature_vdevice_mappings(self) \
            -> Dict[Type[Device], Dict[Feature, Dict[Type[VDevice], Type[Device]]]]:
        return self._abs_setup_feature_vdevice_mappings

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def add_testcase_executor(self, testcase_executor: TestcaseExecutor):
        """
        This method adds a new TestcaseExecutor to the child element list of this object branch
        """
        if not isinstance(testcase_executor, TestcaseExecutor):
            raise TypeError("the given object `testcase_executor` must be of type type `TestcaseExecutor`")
        if testcase_executor in self._testcase_executors:
            raise ValueError("the given object `testcase_executor` already exists in child list")
        self._testcase_executors.append(testcase_executor)

    def determine_feature_replacement_and_vdevice_mappings(self) -> None:
        """
        This method determines the :class:`Feature` replacement and the absolute vdevice mappings for this variation and
        its related features. It determines for every existing scenario-device-feature the related setup-device-feature
        class and sets this information to the property `_feature_replacement`. In addition to that it also determines
        the vDevice-Device mapping that will be assigned for every replaced feature later. This information will be
        saved in the property `_abs_vdevice_mappings`.

        .. note::
            If there is a feature class in the setup device, that is not used in the mapped scenario device, this
            feature will be added as **Autonomous-Feature**. This is required, because the features could be referenced
            in a lower child class than the **instantiated scenario feature**.

        .. note::
            The method automatically searches for the correct mappings. So if there exists more than one possible
            mappings for a feature, the method checks for the defined mapping on scenario level and also on setup level.
            If there are no or more than one possible mappings, the method raises a
            :class:`NotApplicableVariationError`. This error will also be thrown, if there is a vDevice mapping
            expected, while no vDevice mapping exists.

        :raises NotApplicableVariationError: will be thrown if this variation cannot be applied, because the setup-/
                                             scenario-device-features can not be resolved
        """
        feature_replacement = {}
        abs_setup_vdevice_mappings = {}
        for cur_scenario_device, cur_setup_device in self.base_device_mapping.items():
            cur_setup_features = DeviceController.get_for(cur_setup_device).get_all_instantiated_feature_objects()

            if cur_setup_device not in abs_setup_vdevice_mappings.keys():
                abs_setup_vdevice_mappings[cur_setup_device] = {}

            all_assigned_setup_features = []
            cur_scenario_device_orig_features = \
                DeviceController.get_for(cur_scenario_device).get_original_instanced_feature_objects()
            for cur_attr_name, cur_abstract_scenario_feature_obj in cur_scenario_device_orig_features.items():
                replacing_features = [cur_setup_feature for _, cur_setup_feature in cur_setup_features.items()
                                      if isinstance(cur_setup_feature, cur_abstract_scenario_feature_obj.__class__)]
                used_scenario_vdevice, mapped_scenario_device = \
                    cur_abstract_scenario_feature_obj.active_vdevice_device_mapping
                # check if there is a mapped device in scenario level
                cleanup_replacing_features = replacing_features.copy()
                if mapped_scenario_device is not None:
                    # get the related setup device for the mapped scenario device (on scenario level)
                    to_scenarios_vdevice_mapped_setup_device = self.get_setup_device_for(mapped_scenario_device)

                    # now check if there is a mapping on setup level too
                    for cur_replacing_feature in replacing_features:
                        _, mapped_setup_device = cur_replacing_feature.active_vdevice_device_mapping
                        if mapped_setup_device is not None and \
                                mapped_setup_device != to_scenarios_vdevice_mapped_setup_device:
                            # drop this feature matching, because it is not applicable here
                            cleanup_replacing_features.remove(cur_replacing_feature)

                if len(cleanup_replacing_features) != 1:
                    raise NotApplicableVariationError(
                        f'this variation can not be applicable because there was no setup feature implementation of '
                        f'`{cur_abstract_scenario_feature_obj.__class__.__name__}` (used by scenario device '
                        f'`{cur_scenario_device.__name__}`) in setup device `{cur_setup_device.__name__}`')

                if mapped_scenario_device is None:
                    # we have exactly one matching candidate, but also no vDevice mapping
                    # check if the matching candidate has a vDevice mapping
                    _, mapped_setup_device = cleanup_replacing_features[0].active_vdevice_device_mapping
                    cleanup_feature_controller = FeatureController.get_for(cleanup_replacing_features[0].__class__)
                    if mapped_setup_device is None \
                            and len(cleanup_feature_controller.get_abs_inner_vdevice_classes()) > 0:
                        # there is no vDevice mapping on scenario and no vDevice mapping on setup level, but the
                        # feature defined vDevices -> NOT APPLICABLE
                        logger.warning(
                            f"missing vDevice mapping for feature "
                            f"`{cur_abstract_scenario_feature_obj.__class__.__name__}` (used in scenario device "
                            f"`{cur_scenario_device.__name__}` and in setup device `{cur_setup_device.__name__}`) - "
                            f"VARIATION CAN NOT BE APPLIED")
                        raise NotApplicableVariationError(
                            f'this variation can not be applicable because there was no vDevice mapping given on '
                            f'scenario or on setup level for the feature '
                            f'`{cur_abstract_scenario_feature_obj.__class__.__name__}` (used by scenario device '
                            f'`{cur_scenario_device.__name__}`) in setup device `{cur_setup_device.__name__}`')

                all_assigned_setup_features.append(cleanup_replacing_features[0])
                if cur_scenario_device not in feature_replacement.keys():
                    feature_replacement[cur_scenario_device] = {}
                if cur_attr_name not in feature_replacement[cur_scenario_device].keys():
                    cleanup_feature = cleanup_replacing_features[0]
                    cleanup_feature_controller = FeatureController.get_for(cleanup_feature.__class__)

                    used_setup_vdevice, mapped_setup_device = cleanup_feature.active_vdevice_device_mapping

                    # if there is a vDevice mapping on scenario level, but not on setup level, so update the
                    # VDevice-Device-Mapping there
                    if mapped_scenario_device is not None and mapped_setup_device is None:
                        # search the equivalent vDevice on setup level and use this one (we had not to check it,
                        # because check was already done in collector-stage)
                        setup_vdevices = [cur_vdevice for cur_vdevice
                                          in cleanup_feature_controller.get_abs_inner_vdevice_classes()
                                          if cur_vdevice.__name__ == used_scenario_vdevice.__name__]
                        used_setup_vdevice = setup_vdevices[0]
                        # set the mapping
                        abs_setup_vdevice_mappings[cur_setup_device][cleanup_feature] = {
                            used_setup_vdevice: self.get_setup_device_for(mapped_scenario_device)}
                    # if there is a vDevice mapping on setup level, but not on scenario level, so directly update the
                    # VDevice-Device-Mapping there
                    elif mapped_scenario_device is None and mapped_setup_device is not None:
                        abs_setup_vdevice_mappings[cur_setup_device][cleanup_feature] = {
                            used_setup_vdevice: mapped_setup_device}

                    feature_replacement[cur_scenario_device][cur_attr_name] = \
                        (cur_abstract_scenario_feature_obj, cleanup_feature)
            # also add all setup features that are not assigned as autonomous features
            for _, cur_setup_feature in cur_setup_features.items():
                if cur_setup_feature not in all_assigned_setup_features:
                    # determine free name
                    idx = 0
                    autonomous_name = None
                    while autonomous_name is None or autonomous_name in feature_replacement[cur_scenario_device].keys():
                        autonomous_name = f"_autonomous_feat_{idx}"
                        idx += 1
                    feature_replacement[cur_scenario_device][autonomous_name] = (None, cur_setup_feature)

        # set the result to internal properties
        self._feature_replacement = feature_replacement
        self._abs_setup_feature_vdevice_mappings = abs_setup_vdevice_mappings

    def get_setup_device_for(self, scenario_device: Type[Device]) -> Type[Device]:
        """
        This method returns the corresponding Setup-Device for the given Scenario-Device that is contained in the
        mapping of this VariationExecutor.

        :param scenario_device: the scenario device for that the mapped setup device should be returned

        :return: the mapped setup device
        """
        if scenario_device not in self.base_device_mapping.keys():
            raise ValueError(
                f"the given scenario device `{scenario_device.__name__}` is no part of the mapping of this "
                f"VariationExecutor object")
        return self.base_device_mapping[scenario_device]

    def get_scenario_device_for(self, setup_device: Type[Device]) -> Type[Device]:
        """
        This method returns the corresponding Scenario-Device for the given Setup-Device that is contained in the
        mapping of this VariationExecutor.

        :param setup_device: the setup device for that the mapped scenario device should be returned

        :return: the mapped scenario device
        """
        if setup_device not in self.base_device_mapping.values():
            raise ValueError(
                f"the given scenario device `{setup_device.__name__}` is no part of the mapping of this "
                f"VariationExecutor object")
        if list(self.base_device_mapping.values()).count(setup_device) > 1:
            raise KeyError(f"the requested setup device exists more than one time in `base_device_mapping`")
        return [cur_key for cur_key, cur_value in self.base_device_mapping.items() if cur_value == setup_device][0]

    def get_executor_for_testcase(self, testcase: callable) -> Union[TestcaseExecutor, None]:
        """
        This method searches for a TestcaseExecutor in the internal list for which the given testcase method is
        contained in

        :param testcase: the testcase class for which the executor should be searched for

        :return: returns the associated TestcaseExecutor or None if none could be found for the transferred type
        """
        for cur_testcase_executor in self._testcase_executors:
            if cur_testcase_executor.base_testcase_callable == testcase:
                return cur_testcase_executor
        # can not find some
        return None

    def has_feature_implementation_matching(self):
        """
        This method returns True if the features in this variation are valid. For this the setup devices must
        implement all the required features of the scenario device. In other words, a feature child class must be
        implemented in the setup device for each feature in the scenario device.
        """
        for scenario_device, setup_device in self._base_device_mapping.items():
            scenario_device_orig_features = \
                DeviceController.get_for(scenario_device).get_original_instanced_feature_objects()
            for _, cur_scenario_feature in scenario_device_orig_features.items():
                found_setup_feature_for_scenario_feature = False
                setup_device_instantiated_features = \
                    DeviceController.get_for(setup_device).get_all_instantiated_feature_objects()
                for _, cur_setup_feature in setup_device_instantiated_features.items():
                    if isinstance(cur_setup_feature, cur_scenario_feature.__class__):
                        found_setup_feature_for_scenario_feature = True
                if not found_setup_feature_for_scenario_feature:
                    return False
        return True

    def cleanup_empty_executor_branches(self):
        """
        This method searches the whole tree and removes branches where an executor item has no own children. It can
        remove these branches, because they have no valid matchings.

        This method implementation of the :class:`VariationExecutor` does nothing.
        """
        pass

    def has_vdevice_feature_implementation_matching(self) -> bool:
        """
        This method checks for all vDevices that are in the setups/scenario features of this VariationExecutor, if their
        vDevices-Mappings (so the mapped setup-devices) implements all features that are defined in the vDevices

        This method returns false, if there is missing some :class:`Feature` classes.
        """

        for cur_scenario_device, cur_replacement_dict in self.feature_replacement.items():
            cur_setup_device = self.get_setup_device_for(scenario_device=cur_scenario_device)
            all_inner_setup_features = \
                DeviceController.get_for(cur_setup_device).get_all_instantiated_feature_objects()

            # describes the mapping from the new setup feature (key) to the instantiated scenario feature (value)
            #  note that this dictionary only contains the required one
            new_to_old_feature_mapping: Dict[Type[Feature], Feature] = {
                cur_replacement_tuple[1]: cur_replacement_tuple[0]
                for cur_attr_name, cur_replacement_tuple in cur_replacement_dict.items()
                if cur_replacement_tuple[0] is not None}

            # now secure that all features are available in the corresponding setup device, that are defined in the
            #  mapped vDevice
            for _, cur_setup_feature_obj in all_inner_setup_features.items():
                # only check if there is a requirement of this feature (the feature is required by the Scenario)
                if cur_setup_feature_obj.__class__ in new_to_old_feature_mapping.keys():
                    related_scenario_feature_obj = new_to_old_feature_mapping[cur_setup_feature_obj.__class__]
                    # get vDevice and device mapping
                    partner_scenario_vdevice, partner_scenario_device = \
                        related_scenario_feature_obj.active_vdevice_device_mapping
                    if partner_scenario_device is not None and partner_scenario_device is not None:
                        partner_setup_device = self.get_setup_device_for(scenario_device=partner_scenario_vdevice)
                        # get the related vDevice on setup view that is currently active
                        mapped_setup_vdevices = [
                            cur_vdevice for cur_vdevice
                            in FeatureController.get_for(
                                cur_setup_feature_obj.__class__).get_abs_inner_vdevice_classes()
                            if issubclass(cur_vdevice, partner_scenario_vdevice)]
                        if len(mapped_setup_vdevices) != 1:
                            # find no mapping for the vDevice -> not possible
                            return False
                        # now check that the setup partner device has all features implemented that are required
                        # features from the VDevice
                        partner_setup_device_features = \
                            DeviceController.get_for(partner_setup_device).get_all_instantiated_feature_objects()
                        mapped_setup_vdevices_instantiated_features = \
                            VDeviceController.get_for(mapped_setup_vdevices[0]).get_all_instantiated_feature_objects()
                        for _, cur_vdevice_feature in mapped_setup_vdevices_instantiated_features.items():
                            # check that there exists a child feature in the setup device for every used feature in the
                            # vDevice class
                            matchings = [
                                cur_device_feature for _, cur_device_feature in partner_setup_device_features.items()
                                if isinstance(cur_device_feature, cur_vdevice_feature.__class__)]
                            if len(matchings) == 0:
                                return False
        return True

    def has_all_valid_routings(self) -> bool:
        """
        This method returns true if there exist valid routings for every defined connection. Otherwise, it returns
        false.

        :return: returns true if the method finds one or more valid routings for EVERY :class:`Connection`. Otherwise,
                 it returns false
        """
        if self._routings == {}:
            self.determine_absolute_scenario_device_connections()
            self.create_all_valid_routings()
        for cur_conn, cur_routings in self._routings.items():
            if len(cur_routings) == 0:
                return False
        return True

    def update_scenario_device_feature_instances(self):
        """
        This method ensures that the (mostly abstract) feature instances of a scenario are exchanged with the
        feature instances of the assigned setup devices
        """
        for cur_scenario_device, cur_replacement_dict in self.feature_replacement.items():
            for cur_attr_name, cur_replacement_tuple in cur_replacement_dict.items():
                old_instantiated_feature_obj, new_feature_obj = cur_replacement_tuple
                setattr(cur_scenario_device, cur_attr_name, new_feature_obj)

    def revert_scenario_device_feature_instances(self):
        """
        This method ensures that all initialized feature instances of a scenario are set back to the initial given
        features.
        """
        for cur_scenario_device, cur_replacement_dict in self.feature_replacement.items():
            for cur_attr_name, cur_replacement_tuple in cur_replacement_dict.items():
                old_instantiated_feature_obj, new_feature_obj = cur_replacement_tuple
                setattr(cur_scenario_device, cur_attr_name, old_instantiated_feature_obj)

    def update_active_vdevice_device_mappings_in_scenario_and_setup_devices(self):
        """
        This method ensures that the correct `active_vdevices` property in all feature classes of the related setup and
        scenario-device classes are set correctly.
        """

        for cur_setup_device, feature_dict in self.abs_setup_feature_vdevice_mappings.items():
            if cur_setup_device not in self._original_active_vdevice_mappings.keys():
                self._original_active_vdevice_mappings[cur_setup_device] = {}
            for cur_setup_feature, mapping_dict in feature_dict.items():

                cur_setup_feature_vdevice = list(mapping_dict.keys())[0]
                cur_mapped_setup_device = list(mapping_dict.values())[0]

                # first save old value to revert it later
                self._original_active_vdevice_mappings[cur_setup_device][cur_setup_feature] = \
                    cur_setup_feature.active_vdevices
                # now set new value
                cur_setup_feature.active_vdevices = {cur_setup_feature_vdevice: cur_mapped_setup_device}

                # now also determine the mapping for the scenario-feature (if there exists one)
                cur_scenario_device = self.get_scenario_device_for(cur_setup_device)
                cur_scenario_feature = None
                for cur_replacement_scenario_feature, cur_replacement_setup_feature in \
                        self.feature_replacement[cur_scenario_device].values():
                    if cur_replacement_setup_feature == cur_setup_feature:
                        cur_scenario_feature = cur_replacement_scenario_feature
                        break
                if cur_scenario_feature is None:
                    # there exists no scenario feature -> we can ignore this
                    pass
                else:
                    cur_scenario_feature_controller = FeatureController.get_for(cur_scenario_feature.__class__)
                    # now get the same vdevice (same name) but on scenario level
                    cur_scenario_feature_vdevice = [
                        cur_vdevice for cur_vdevice in cur_scenario_feature_controller.get_abs_inner_vdevice_classes()
                        if cur_vdevice.__name__ == cur_setup_feature_vdevice.__name__]
                    if len(cur_scenario_feature_vdevice) == 1:
                        # only if there exists exactly one scenario vdevice with the same name

                        if cur_scenario_device not in self._original_active_vdevice_mappings.keys():
                            self._original_active_vdevice_mappings[cur_scenario_device] = {}
                        # first save old value to revert it later
                        self._original_active_vdevice_mappings[cur_scenario_device][cur_scenario_feature] = \
                            cur_scenario_feature.active_vdevices
                        # now set new value
                        cur_scenario_feature.active_vdevices = \
                            {cur_scenario_feature_vdevice[0]: self.get_scenario_device_for(cur_mapped_setup_device)}

    def revert_active_vdevice_device_mappings_in_scenario_and_setup_devices(self):
        """
        This method ensures that the `active_vdevices` property that was changed with
        `update_active_vdevice_device_mappings()` will be reverted correctly.
        """
        for cur_scenario_or_setup_device, cur_feature_mapping_dict in self._original_active_vdevice_mappings.items():
            for cur_feature, cur_original_mapping in cur_feature_mapping_dict.items():
                cur_feature.active_vdevices = cur_original_mapping

    def update_inner_referenced_feature_instances(self):
        """
        This method ensures that all inner referenced feature instances of the used feature object, will be replaced
        with the related feature instances of the device object itself.

        .. note::
            Note that this method expects that the true defined scenario features are already replaced with the real
            setup features. So the method requires that the method `update_scenario_device_feature_instances()` was
            called before.
        """
        for scenario_device, _ in self._base_device_mapping.items():
            # these features are subclasses of the real defined one (because they are already the replaced ones)
            all_device_features = DeviceController.get_for(scenario_device).get_all_instantiated_feature_objects()
            all_instantiated_feature_objs = [cur_feature for _, cur_feature in all_device_features.items()]
            for cur_feature_name, cur_feature in all_device_features.items():
                cur_feature_controller = FeatureController.get_for(cur_feature.__class__)
                # now check the inner referenced features of this feature and check if that exists in the device
                for cur_ref_feature_name, cur_ref_feature in \
                        cur_feature_controller.get_inner_referenced_features().items():
                    potential_candidates = [candidate_feature for candidate_feature in all_instantiated_feature_objs
                                            if isinstance(candidate_feature, cur_ref_feature.__class__)]
                    if len(potential_candidates) != 1:
                        raise RuntimeError("found none or more than one potential replacing candidates")
                    replacing_candidate = potential_candidates[0]
                    # because `cur_feature` is only the object instance, the value will be overwritten only for this
                    # object
                    setattr(cur_feature, cur_ref_feature_name, replacing_candidate)

    def update_vdevice_referenced_feature_instances(self):
        """
        This method ensures that all referenced feature instances in every active vDevice classes of the used feature
        objects, will be replaced with the related feature instances of the mapped device object.

        .. note::
            Note that this method expects that the true defined scenario features are already replaced with the real
            setup features. In addition to that, the method expects, that the vDevice-Device mapping of every feature
            was set to the resolved setup device! So the method requires that the method
            `update_scenario_device_feature_instances()` was called before.
        """
        for scenario_device, _ in self._base_device_mapping.items():
            # these features are subclasses of the real defined one (because they are already the replaced ones)
            all_device_features = DeviceController.get_for(scenario_device).get_all_instantiated_feature_objects()
            for _, cur_feature in all_device_features.items():
                # now get the related vDevice class and update its attributes
                cur_vdevice, cur_device = cur_feature.active_vdevice_device_mapping
                if cur_vdevice is not None and cur_device is not None:
                    cur_vdevice_controller = VDeviceController.get_for(cur_vdevice)
                    cur_vdevice_all_features = cur_vdevice_controller.get_original_instanced_feature_objects()
                    cur_device_all_features = cur_vdevice_controller.get_all_instantiated_feature_objects()
                    for cur_vdevice_attr_name, cur_vdevice_feature in cur_vdevice_all_features.items():
                        # now search the used feature in the mapped device itself
                        potential_candidates = [
                            candidate_feature for _, candidate_feature in cur_device_all_features.items()
                            if isinstance(candidate_feature, cur_vdevice_feature.__class__)]
                        if len(potential_candidates) != 1:
                            raise RuntimeError("found none or more than one potential replacing candidates")
                        replacing_candidate = potential_candidates[0]
                        # because `cur_feature` is only the object instance, the value will be overwritten only for this
                        # object
                        setattr(cur_vdevice, cur_vdevice_attr_name, replacing_candidate)

    def can_be_applied(self) -> bool:
        """
        This method returns True if this Variation is executable. First the method checks if all defined
        :class:`Feature` instances are available and fully implemented in the mapped setup :class:`Device`.
        Furthermore, it checks if their exists a valid routing which also matches the defined class `@for_vdevice`
        definition of the used :class:`Feature` classes.
        """
        try:
            self.determine_feature_replacement_and_vdevice_mappings()
        except NotApplicableVariationError:
            # this variation can not be used, because the features can not be resolved correctly!
            return False

        if not self.has_feature_implementation_matching():
            return False
        if not self.has_vdevice_feature_implementation_matching():
            return False
        if not self.has_all_valid_routings():
            return False
        return True

    def determine_absolute_scenario_device_connections(self):
        """
        This method determines the variation absolute connections for this variation and sets them to the internal
        properties `_abs_variation_*_device_connections`. This will be used to determine the real connection-subtree
        (that can be used for this variation) by the method `create_all_valid_routings()`.

        The method re-executes the algorithm to determine the absolute connections for a scenario/setup (see the method
        :meth:`Collector.determine_absolute_device_connections_for`), but it considers the real applied vDevice and
        their feature restrictions too.
        """
        abs_var_scenario_device_cnns = {}

        # first determine all relevant absolute connection depending on the current scenario
        for cur_scenario_device, _ in self.base_device_mapping.items():
            cur_scenario_device_abs_cnns = \
                DeviceController.get_for(cur_scenario_device).get_all_absolute_connections()
            for _, cur_cnn_list in cur_scenario_device_abs_cnns.items():
                for cur_cnn in cur_cnn_list:
                    if cur_scenario_device not in abs_var_scenario_device_cnns.keys():
                        abs_var_scenario_device_cnns[cur_scenario_device] = {}

                    if cur_cnn.from_device == cur_scenario_device:
                        cur_to_device = cur_cnn.to_device
                    else:
                        cur_to_device = cur_cnn.from_device

                    if cur_to_device not in abs_var_scenario_device_cnns[cur_scenario_device].keys():
                        abs_var_scenario_device_cnns[cur_scenario_device][cur_to_device] = []

                    abs_var_scenario_device_cnns[cur_scenario_device][cur_to_device].append(cur_cnn)

        # now iterate over every feature, that is used by the scenario and determine the class-based feature connections
        # of the mapped scenario feature (and its vDevice)
        for cur_setup_device, feature_dict in self.abs_setup_feature_vdevice_mappings.items():
            cur_scenario_device = self.get_scenario_device_for(cur_setup_device)
            for cur_setup_feature, mapping_dict in feature_dict.items():
                feature_replacement = {
                    cur_tuple[1]: cur_tuple[0] for _, cur_tuple in self.feature_replacement[cur_scenario_device].items()
                }
                cur_scenario_feature: Feature = feature_replacement[cur_setup_feature]
                cur_setup_feature_vdevice = list(mapping_dict.keys())[0]
                cur_mapped_setup_device = list(mapping_dict.values())[0]
                cur_mapped_scenario_device = self.get_scenario_device_for(cur_mapped_setup_device)

                # get relevant class based connections for the current feature on setup level (this is really be used
                # here)
                feature_cnns = \
                    FeatureController.get_for(
                        cur_setup_feature.__class__).get_class_based_for_vdevice()[cur_setup_feature_vdevice]
                # connection that are relevant for this feature
                relevant_cnns = abs_var_scenario_device_cnns[cur_scenario_device][cur_mapped_scenario_device]

                relevant_device_cnn = None

                if len(relevant_cnns) > 1:
                    # we have parallel possibilities -> determine the selected one (only one is allowed to fit)
                    for cur_relevant_cnn in relevant_cnns:
                        for cur_relevant_single_cnn in cur_relevant_cnn.get_singles():
                            for cur_feature_cnn in feature_cnns:
                                for cur_feature_single_cnn in cur_feature_cnn.get_singles():
                                    if cur_feature_single_cnn.contained_in(cur_relevant_single_cnn):
                                        if relevant_device_cnn is not None:
                                            raise UnclearAssignableFeatureConnectionError(
                                                f"the devices {cur_scenario_device.__name__} and "
                                                f"{cur_mapped_scenario_device.__name__} have multiple parallel "
                                                f"connections - the device `{cur_scenario_device.__name__}` uses a "
                                                f"feature `{cur_scenario_feature.__class__.__name__}` that matches "
                                                f"with the device `{cur_mapped_scenario_device.__name__}`, but it is "
                                                f"not clear which of the parallel connection could be used"
                                            )
                                        relevant_device_cnn = cur_relevant_cnn
                elif len(relevant_cnns) == 1:
                    relevant_device_cnn = relevant_cnns[0]
                if relevant_device_cnn is None:
                    # todo this does not map here
                    raise ValueError("can not find matching connection on scenario level")

                # now cleanup the scenario-device connection `relevant_device_cnn` according to the class-based feature
                # connection
                new_cleaned_singles = []
                for cur_old_cnn_single in relevant_device_cnn.get_singles():
                    for cur_feature_cnn in feature_cnns:
                        if cur_feature_cnn.contained_in(cur_old_cnn_single, ignore_metadata=True):
                            new_cleaned_singles.append(cur_old_cnn_single)

                new_cnn_to_replace = Connection.based_on(*new_cleaned_singles)
                new_cnn_to_replace.set_metadata_for_all_subitems(new_cleaned_singles[0].metadata)

                abs_var_scenario_device_cnns[cur_scenario_device][cur_mapped_scenario_device].remove(
                    relevant_device_cnn)
                abs_var_scenario_device_cnns[cur_scenario_device][cur_mapped_scenario_device].append(new_cnn_to_replace)

                # also search the connection in the other direction
                other_dir_relevant_device_cnn = None
                for cur_cnn in abs_var_scenario_device_cnns[cur_mapped_scenario_device][cur_scenario_device]:
                    if cur_cnn.equal_with(relevant_device_cnn):
                        other_dir_relevant_device_cnn = cur_cnn
                        break
                # and also replace it
                abs_var_scenario_device_cnns[cur_mapped_scenario_device][cur_scenario_device].remove(
                    other_dir_relevant_device_cnn)
                abs_var_scenario_device_cnns[cur_mapped_scenario_device][cur_scenario_device].append(new_cnn_to_replace)

        # set the determined values in variation object
        self._abs_variation_scenario_device_connections = []
        for _, from_device_dict in abs_var_scenario_device_cnns.items():
            for _, cur_cnn_list in from_device_dict.items():
                for cur_cnn in cur_cnn_list:
                    self._abs_variation_scenario_device_connections.append(cur_cnn)

    def create_all_valid_routings(self):
        """
        This method determines all valid routings for the current variation. It iterates over every defined
        absolute determined :class:`Connection` in the :class:`Scenario` class and trys to find a valid routing for it.

        .. note::
            The method assigns a full report with all valid routings into the local property `_routings`.
        """
        self._routings = {}
        for scenario_device, setup_device in self._base_device_mapping.items():
            for cur_scenario_conn in self._abs_variation_scenario_device_connections:
                if cur_scenario_conn.has_connection_from_to(scenario_device):
                    # only check if the connection object has not yet been investigated
                    if cur_scenario_conn not in self._routings.keys():
                        # try to find a routing for the current connection
                        founded_routings = RoutingPath.route_through(
                            cur_scenario_conn, self._base_device_mapping)
                        self._routings[cur_scenario_conn] = founded_routings

    def determine_abs_variation_connections(self):
        """
        This method determines the absolute variation connections, that will be saved in the property
        :meth:`VariationExecutor._abs_variation_connections`. This is the INTERSECTION between the active absolute
        scenario connection for this variation (see
        :meth:`VariationExecutor._abs_variation_scenario_device_connections`) and the virtual possible connections of
        the possible routings (multiple routings will be combined over an OR relation).

        This determined connection can directly be used to determine active method variations.
        """
        virtual_routing_cnns = {}
        for cur_cnn, cur_routing_list in self._routings.items():
            virtual_routing_cnns[cur_cnn] = None
            for cur_routing in cur_routing_list:
                virtual_cnn = cur_routing.get_virtual_connection()

                if virtual_routing_cnns[cur_cnn] is None:
                    virtual_routing_cnns[cur_cnn] = Connection.based_on(*virtual_cnn)
                else:
                    virtual_routing_cnns[cur_cnn] = Connection.based_on(virtual_routing_cnns[cur_cnn], *virtual_cnn)
                virtual_routing_cnns[cur_cnn].set_metadata_for_all_subitems(virtual_cnn[0].metadata)

        self._abs_variation_connections = []
        for cur_cnn in self._abs_variation_scenario_device_connections:
            cur_virtual_cnn = virtual_routing_cnns[cur_cnn]
            new_intersection = cur_cnn.intersection_with(cur_virtual_cnn)
            new_intersection.set_metadata_for_all_subitems(None)
            # always set the metadata for setup devices
            new_intersection.set_metadata_for_all_subitems(cur_virtual_cnn.metadata)
            self._abs_variation_connections.append(new_intersection)

    def set_conn_dependent_methods(self):
        """
        This method sets a clear method instance for all method variations.

        .. note::
            It is important to call the method :meth:`VariationExecutor.determine_abs_variation_connections` and
            the method :meth:`VariationExecutor.update_scenario_device_feature_instances` before!
        """
        for scenario_device, setup_device in self._base_device_mapping.items():
            setup_device_instantiated_features = \
                DeviceController.get_for(setup_device).get_all_instantiated_feature_objects()
            for cur_attr_name, cur_setup_feature in setup_device_instantiated_features.items():

                cur_setup_feature_controller = FeatureController.get_for(cur_setup_feature.__class__)
                method_var_data_of_feature = cur_setup_feature_controller.get_method_based_for_vdevice()
                if method_var_data_of_feature is None:
                    # ignore if no method-variations exists for the current feature
                    continue

                method_var_selection = {}

                for cur_method_name, cur_method in inspect.getmembers(
                        cur_setup_feature, lambda o: inspect.isfunction(o) or inspect.ismethod(o)):

                    if cur_method_name not in method_var_data_of_feature.keys():
                        # ignore if there was no method-variation registration for the current method
                        continue

                    mapped_vdevice, mapped_setup_device = cur_setup_feature.active_vdevice_device_mapping
                    # get all absolute connections for this setup device
                    relevant_abs_conn = []
                    for cur_cnn in self._abs_variation_connections:
                        if cur_cnn.has_connection_from_to(start_device=setup_device, end_device=mapped_setup_device):
                            relevant_abs_conn.append(cur_cnn)
                    if len(relevant_abs_conn) is None:
                        raise RuntimeError(f"detect empty absolute connection between device `{setup_device.__name__}` "
                                           f"and device `{mapped_setup_device.__name__}`")
                    absolute_feature_method_var_cnn = Connection.based_on(*relevant_abs_conn)
                    cur_method_variation = cur_setup_feature_controller.get_method_variation(
                        of_method_name=cur_method_name, for_vdevice=mapped_vdevice,
                        with_connection=absolute_feature_method_var_cnn)
                    if cur_method_variation is None:
                        raise AttributeError(f"can not find a valid method variation for method `{cur_method_name}` "
                                             f"of feature `{cur_setup_feature.__class__.__name__}`")
                    method_var_selection[cur_method_name] = \
                        (mapped_vdevice, absolute_feature_method_var_cnn, cur_method_variation)

                cur_setup_feature._active_method_variations = method_var_selection

    def execute(self) -> None:
        """
        This method executes this branch of the tree
        """

        print(f"    VARIATION ", end='')
        device_map_str = [f"{scenario_device.__qualname__}:{setup_device.__qualname__}"
                          for scenario_device, setup_device in self._base_device_mapping.items()]
        print(' | '.join(device_map_str))
        try:
            try:
                self.determine_abs_variation_connections()
                self.update_scenario_device_feature_instances()
                self.update_active_vdevice_device_mappings_in_scenario_and_setup_devices()
                self.update_inner_referenced_feature_instances()
                self.update_vdevice_referenced_feature_instances()
                self.set_conn_dependent_methods()

                self.fixture_manager.enter(self)

                for cur_testcase_executor in self.testcase_executors:
                    if cur_testcase_executor.has_runnable_elements():

                        cur_testcase_executor.execute()
                    elif cur_testcase_executor.prev_mark == PreviousExecutorMark.SKIP:
                        cur_testcase_executor.set_result_for_whole_branch(ResultState.SKIP)
                    elif cur_testcase_executor.prev_mark == PreviousExecutorMark.COVERED_BY:
                        cur_testcase_executor.set_result_for_whole_branch(ResultState.COVERED_BY)
                    else:
                        cur_testcase_executor.set_result_for_whole_branch(ResultState.NOT_RUN)
            except:
                # we can catch everything, because error is already documented
                traceback.print_exception(*sys.exc_info())
            if self.fixture_manager.is_allowed_to_leave(self):
                self.fixture_manager.leave(self)
        except:
            # we can catch everything, because error is already documented
            traceback.print_exception(*sys.exc_info())
        finally:
            self.revert_active_vdevice_device_mappings_in_scenario_and_setup_devices()
            self.revert_scenario_device_feature_instances()
