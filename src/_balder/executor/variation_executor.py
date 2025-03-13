from __future__ import annotations

from typing import Type, Union, List, Dict, TYPE_CHECKING

import inspect
import logging
from _balder.cnnrelations import OrConnectionRelation
from _balder.device import Device
from _balder.connection import Connection
from _balder.feature_replacement_mapping import FeatureReplacementMapping
from _balder.fixture_execution_level import FixtureExecutionLevel
from _balder.testresult import ResultState, BranchBodyResult, ResultSummary
from _balder.executor.basic_executable_executor import BasicExecutableExecutor
from _balder.executor.testcase_executor import TestcaseExecutor
from _balder.executor.unresolved_parametrized_testcase_executor import UnresolvedParametrizedTestcaseExecutor
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.routing_path import RoutingPath
from _balder.unmapped_vdevice import UnmappedVDevice
from _balder.feature_vdevice_mapping import FeatureVDeviceMapping
from _balder.controllers import DeviceController, VDeviceController, FeatureController, NormalScenarioSetupController
from _balder.exceptions import NotApplicableVariationException, UnclearAssignableFeatureConnectionError

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.feature import Feature
    from _balder.scenario import Scenario
    from _balder.controllers.scenario_controller import ScenarioController
    from _balder.controllers.setup_controller import SetupController
    from _balder.executor.scenario_executor import ScenarioExecutor
    from _balder.fixture_manager import FixtureManager


logger = logging.getLogger(__file__)


class VariationExecutor(BasicExecutableExecutor):
    """
    A VariationExecutor only contains :meth:`TestcaseExecutor` children.
    """
    fixture_execution_level = FixtureExecutionLevel.VARIATION

    def __init__(self, device_mapping: Dict[Type[Device], Type[Device]], parent: ScenarioExecutor):
        super().__init__()
        self._testcase_executors = []
        self._base_device_mapping = device_mapping
        self._parent_executor = parent
        self._fixture_manager = parent.fixture_manager

        # contains the active routings for the current variation
        self._routings: Dict[Connection, List[RoutingPath]] = {}
        # buffer variable to save the feature replacement after it was determined with
        # `determine_feature_replacement_and_vdevice_mappings()`
        self._feature_replacement: Union[None, Dict[Type[Device], FeatureReplacementMapping]] = None
        # buffer variable to save the feature replacement after it was determined with
        # `determine_feature_replacement_and_vdevice_mappings()`
        self._abs_setup_feature_vdevice_mappings: Union[None, Dict[Type[Device], FeatureVDeviceMapping]] = None

        # contains the absolute scenario device connections for the current variation
        self._abs_variation_scenario_device_connections: Union[List[Connection], None] = None
        # contains the absolute active variation connections (intersection between scenario based
        # `_abs_variation_scenario_device_connections` and virtual connection from active RoutingPath objects from
        # `_routings`)
        self._abs_variation_connections: Union[List[Connection], None] = None

        # contains the original active vdevice mappings for all scenario and setup devices (will be managed by
        # `update_active_vdevice_device_mappings_in_scenario_and_setup_devices()` and
        # `revert_active_vdevice_device_mappings_in_scenario_and_setup_devices()`)
        self._original_active_vdevice_mappings: Dict[Type[Device], FeatureVDeviceMapping] = {}

        # is True if the applicability check was done
        self._applicability_check_done = False
        #: this property holds the exception of type :class:`NotApplicableVariationException` if the variation can not
        #:  be applied, otherwise this property is None
        self._not_applicable_variation_exc = None

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
    def cur_scenario_controller(self) -> ScenarioController:
        """
        returns the current :class:`ScenarioController` for this variation
        """
        return self._parent_executor.base_scenario_controller

    @property
    def cur_setup_class(self) -> Setup:
        """property returns the current :class:`Setup` for this variation"""
        return self._parent_executor.parent_executor.base_setup_class

    @property
    def cur_setup_controller(self) -> SetupController:
        """
        returns the current :class:`SetupController` for this variation
        """
        return self._parent_executor.parent_executor.base_setup_controller

    @property
    def base_device_mapping(self) -> Dict[Type[Device], Type[Device]]:
        """
        property returns the device mapping which is a dictionary with the scenario devices as keys and their related
        setup devices as values
        """
        return self._base_device_mapping

    @property
    def all_child_executors(self) -> List[TestcaseExecutor | UnresolvedParametrizedTestcaseExecutor]:
        return self._testcase_executors

    @property
    def fixture_manager(self) -> FixtureManager:
        """returns the active fixture manager"""
        return self._fixture_manager

    @property
    def feature_replacement(self) -> Dict[Type[Device], FeatureReplacementMapping]:
        """
        this property is a dictionary with every scenario device as key and feature-replacement-mapping as value - the
        mappings hold at least information about the attribute name of the feature in scenario device, the old
        scenario-feature the instantiated feature from the scenario if it exists, otherwise this is None) and the
        new feature as second item (the feature of the related Setup-Device)
        """
        return self._feature_replacement

    @property
    def abs_setup_feature_vdevice_mappings(self) -> Dict[Type[Device], FeatureVDeviceMapping]:
        """returns the feature replacement that was determined with
        `determine_feature_replacement_and_vdevice_mappings()`"""
        return self._abs_setup_feature_vdevice_mappings

    @property
    def not_applicable_variation_exc(self) -> Union[NotApplicableVariationException, None]:
        """holds the :class:`NotApplicableVariationException` that describes why this variation in not applicable"""
        return self._not_applicable_variation_exc

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _prepare_execution(self, show_discarded):
        print("    VARIATION ", end='')
        device_map_str = [f"{scenario_device.__qualname__}:{setup_device.__qualname__}"
                          for scenario_device, setup_device in self._base_device_mapping.items()]
        print(' | '.join(device_map_str))
        if show_discarded and not self.can_be_applied():
            print(f"      DISCARDED BECAUSE `{self.not_applicable_variation_exc.args[0]}`")
        else:
            self.determine_abs_variation_connections()
            self.update_scenario_device_feature_instances()
            self.update_active_vdevice_device_mappings_in_all_features()
            self.exchange_unmapped_vdevice_references()
            self.update_vdevice_referenced_feature_instances()
            self.set_conn_dependent_methods()
            self.resolve_and_exchange_unresolved_parametrization()

    def _body_execution(self, show_discarded):
        if show_discarded and not self.can_be_applied():
            # do nothing if this variation can not be applied (is discarded)
            return

        for cur_testcase_executor in self.get_testcase_executors():
            if (cur_testcase_executor.has_runnable_tests()
                    or cur_testcase_executor.has_skipped_tests()
                    or cur_testcase_executor.has_covered_by_tests()):
                cur_testcase_executor.execute()
            else:
                cur_testcase_executor.set_result_for_whole_branch(ResultState.NOT_RUN)

    def _cleanup_execution(self, show_discarded):
        if show_discarded and not self.can_be_applied():
            # do nothing if this variation can not be applied (is discarded)
            return

        self.restore_original_vdevice_references()
        self.revert_active_vdevice_device_mappings_in_all_features()
        self.revert_scenario_device_feature_instances()

    def _verify_applicability_trough_feature_implementation_matching(self):
        """
        This method validates, that the features in this variation are valid. For this the setup devices must
        implement all the required features of the scenario device. In other words, a feature child class must be
        implemented in the setup device for each feature in the scenario device.
        """
        for scenario_device, setup_device in self._base_device_mapping.items():
            scenario_device_orig_features = \
                DeviceController.get_for(scenario_device).get_original_instanced_feature_objects()
            for cur_scenario_feature_attr_name, cur_scenario_feature in scenario_device_orig_features.items():
                found_setup_feature_for_scenario_feature = False
                setup_device_instantiated_features = \
                    DeviceController.get_for(setup_device).get_all_instantiated_feature_objects()
                for _, cur_setup_feature in setup_device_instantiated_features.items():
                    if isinstance(cur_setup_feature, cur_scenario_feature.__class__):
                        found_setup_feature_for_scenario_feature = True
                if not found_setup_feature_for_scenario_feature:
                    raise NotApplicableVariationException(
                        f'no matching setup-level feature found for scenario-level feature '
                        f'`{cur_scenario_feature_attr_name} = {cur_scenario_feature.__class__.__name__}()` of device '
                        f'`{scenario_device.__qualname__}`')

    def _verify_applicability_trough_vdevice_feature_impl_matching(self) -> None:
        """
        This method checks for all vDevices that are in the setups/scenario features of this VariationExecutor, if their
        vDevices-Mappings (so the mapped setup-devices) implements all features that are defined in the vDevices
        """

        for cur_scenario_device, cur_replacement_mapping in self.feature_replacement.items():
            cur_setup_device = self.get_setup_device_for(scenario_device=cur_scenario_device)
            all_inner_setup_features = \
                DeviceController.get_for(cur_setup_device).get_all_instantiated_feature_objects()

            # now secure that all features are available in the corresponding setup device, that are defined in the
            #  mapped vDevice
            for _, cur_setup_feature_obj in all_inner_setup_features.items():
                related_scenario_feature_obj = \
                    cur_replacement_mapping.get_replaced_scenario_feature_for(cur_setup_feature_obj)

                # only check if this feature is required by the scenario
                if related_scenario_feature_obj is None:
                    # ignore this, because this feature is not used in the scenario
                    continue

                # get vDevice and device mapping
                partner_scenario_vdevice, partner_scenario_device = \
                    related_scenario_feature_obj.active_vdevice_device_mapping

                if partner_scenario_device is None:
                    # ignore because no mapping exist here
                    continue

                partner_setup_device = self.get_setup_device_for(scenario_device=partner_scenario_device)
                # get the related vDevice on setup view that is currently active
                mapped_setup_vdevices = [
                    cur_vdevice for cur_vdevice
                    in FeatureController.get_for(
                        cur_setup_feature_obj.__class__).get_abs_inner_vdevice_classes()
                    if issubclass(cur_vdevice, partner_scenario_vdevice)]
                if len(mapped_setup_vdevices) != 1:
                    # find no mapping for the vDevice -> not possible
                    # todo optimize this exception message
                    raise NotApplicableVariationException(
                        f'can not find a valid setup-level vDevice in setup feature '
                        f'`{cur_setup_feature_obj.__class__}`')
                # now check that the setup partner device has all features implemented that are required
                # features from the VDevice
                partner_setup_device_features = \
                    DeviceController.get_for(partner_setup_device).get_all_instantiated_feature_objects()
                mapped_setup_vdevices_instantiated_features = \
                    VDeviceController.get_for(mapped_setup_vdevices[0]).get_all_instantiated_feature_objects()
                for _, cur_vdevice_feature in mapped_setup_vdevices_instantiated_features.items():
                    # check that there exists a child feature in the setup device for every used feature in the
                    # vDevice class
                    if len([cur_device_feature for _, cur_device_feature in partner_setup_device_features.items()
                            if isinstance(cur_device_feature, cur_vdevice_feature.__class__)]) == 0:
                        raise NotApplicableVariationException(
                            f'can not find a child feature in mapped setup device `{partner_setup_device.__qualname__}`'
                            f' for required feature `{cur_vdevice_feature.__class__}` of vDevice '
                            f'`{mapped_setup_vdevices[0].__qualname__}`')

    def _verify_applicability_trough_all_valid_routings(self) -> None:
        """
        This method ensures that valid routings exist for every defined connection.

        The check is passed, if the method finds one or more valid routings for EVERY scenario-level
        :class:`Connection`.
        """
        if not self._routings:
            self.determine_absolute_scenario_device_connections()
            self.create_all_valid_routings()
        for scenario_cnn, cur_routings in self._routings.items():
            if len(cur_routings) == 0:
                raise NotApplicableVariationException(
                    f'can not find a valid routing on setup level for the connection `{scenario_cnn.get_tree_str()}` '
                    f'between scenario devices `{scenario_cnn.from_device}` and `{scenario_cnn.to_device}`')

    def _get_matching_setup_features_for(
            self,
            scenario_feature_obj: Feature,
            in_setup_device: Type[Device]
    ) -> List[Feature]:
        """
        Helper method that returns all matching setup features for the provided scenario feature in the provided setup
        device.
        """
        cur_setup_features = DeviceController.get_for(in_setup_device).get_all_instantiated_feature_objects()

        replacing_feature_candidates = [
            cur_setup_feature for cur_setup_feature in cur_setup_features.values()
            if isinstance(cur_setup_feature, scenario_feature_obj.__class__)
        ]
        active_scenario_vdev, mapped_scenario_dev = scenario_feature_obj.active_vdevice_device_mapping

        replacing_features = replacing_feature_candidates.copy()
        if mapped_scenario_dev is not None:
            # get the related setup device for the mapped scenario device (on scenario level)
            setup_dev_of_mapped_scenario_dev = self.get_setup_device_for(mapped_scenario_dev)

            # now check if there is a mapping on setup level too
            for cur_replacing_feature in replacing_feature_candidates:
                mapped_setup_vdev, mapped_setup_dev = cur_replacing_feature.active_vdevice_device_mapping
                if mapped_setup_vdev is not None and not issubclass(mapped_setup_vdev, active_scenario_vdev):
                    # drop this feature matching, because we have different vdevice mapped
                    replacing_features.remove(cur_replacing_feature)
                elif mapped_setup_dev is not None and mapped_setup_dev != setup_dev_of_mapped_scenario_dev:
                    # drop this feature matching, because it is not applicable here
                    replacing_features.remove(cur_replacing_feature)
        return replacing_features

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def testsummary(self) -> ResultSummary:
        if self.can_be_applied():
            return super().testsummary()
        return ResultSummary()

    def get_testcase_executors(self) -> List[TestcaseExecutor | UnresolvedParametrizedTestcaseExecutor]:
        """returns all sub testcase executors that belongs to this variation-executor"""
        return self._testcase_executors.copy()

    def add_testcase_executor(self, testcase_executor: TestcaseExecutor | UnresolvedParametrizedTestcaseExecutor):
        """
        This method adds a new TestcaseExecutor to the child element list of this object branch
        """
        if not isinstance(testcase_executor, (TestcaseExecutor, UnresolvedParametrizedTestcaseExecutor)):
            raise TypeError("the given object `testcase_executor` must be of type type `TestcaseExecutor` or "
                            "`UnresolvedParametrizedTestcaseExecutor`")
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
        feature_replacement = {
            scenario_dev: FeatureReplacementMapping() for scenario_dev in self.base_device_mapping.keys()
        }

        abs_setup_vdevice_mappings = {
            setup_dev: FeatureVDeviceMapping() for setup_dev in self.base_device_mapping.values()
        }
        for cur_scenario_device, cur_setup_device in self.base_device_mapping.items():

            for cur_attr_name, cur_scenario_feature_obj in \
                    DeviceController.get_for(cur_scenario_device).get_all_instantiated_feature_objects().items():
                active_scenario_vdevice, mapped_scenario_device = cur_scenario_feature_obj.active_vdevice_device_mapping

                cur_setup_feature_objs = self._get_matching_setup_features_for(
                    scenario_feature_obj=cur_scenario_feature_obj, in_setup_device=cur_setup_device
                )

                if len(cur_setup_feature_objs) != 1:
                    raise NotApplicableVariationException(
                        f'this variation can not be applicable because there was no setup feature implementation of '
                        f'`{cur_scenario_feature_obj.__class__.__name__}` (used by scenario device '
                        f'`{cur_scenario_device.__name__}`) in setup device `{cur_setup_device.__name__}`')
                cur_setup_feature_obj = cur_setup_feature_objs[0]

                all_abs_inner_vdevs_of_setup = \
                    FeatureController.get_for(cur_setup_feature_obj.__class__).get_abs_inner_vdevice_classes()
                used_setup_vdevice, mapped_setup_device = cur_setup_feature_obj.active_vdevice_device_mapping

                if mapped_scenario_device is None:
                    # we have exactly one matching candidate, but also no vDevice mapping
                    # check if the matching candidate has a vDevice mapping
                    if mapped_setup_device is None and len(all_abs_inner_vdevs_of_setup) > 0:
                        # there is no vDevice mapping on scenario and no vDevice mapping on setup level, but the
                        # feature defined vDevices -> NOT APPLICABLE
                        logger.warning(
                            f"missing vDevice mapping for feature "
                            f"`{cur_scenario_feature_obj.__class__.__name__}` (used in scenario device "
                            f"`{cur_scenario_device.__name__}` and in setup device `{cur_setup_device.__name__}`) - "
                            f"VARIATION CAN NOT BE APPLIED")
                        raise NotApplicableVariationException(
                            f'this variation can not be applied because there was no vDevice mapping given on '
                            f'scenario or on setup level for the feature '
                            f'`{cur_scenario_feature_obj.__class__.__name__}` (used by scenario device '
                            f'`{cur_scenario_device.__name__}`) in setup device `{cur_setup_device.__name__}`')

                if cur_attr_name not in feature_replacement[cur_scenario_device].attr_names:

                    # if there is a vDevice mapping on scenario level, but not on setup level, so update the
                    # VDevice-Device-Mapping there
                    if mapped_scenario_device is not None and mapped_setup_device is None:
                        # search the equivalent vDevice on setup level and use this one (we had not to check it,
                        # because check was already done in collector-stage)
                        setup_vdevices = [cur_vdevice for cur_vdevice in all_abs_inner_vdevs_of_setup
                                          if cur_vdevice.__name__ == active_scenario_vdevice.__name__]
                        used_setup_vdevice = setup_vdevices[0]
                        # set the mapping
                        abs_setup_vdevice_mappings[cur_setup_device].add(
                            feature=cur_setup_feature_obj,
                            mappings={
                                used_setup_vdevice: self.get_setup_device_for(mapped_scenario_device)
                            }
                        )
                    # if there is a vDevice mapping on setup level, but not on scenario level, so directly update the
                    # VDevice-Device-Mapping there
                    elif mapped_scenario_device is None and mapped_setup_device is not None:
                        abs_setup_vdevice_mappings[cur_setup_device].add(
                            feature=cur_setup_feature_obj,
                            mappings={
                                used_setup_vdevice: mapped_setup_device
                            }
                        )

                    feature_replacement[cur_scenario_device].add(attr_name=cur_attr_name,
                                                                 scenario_feature=cur_scenario_feature_obj,
                                                                 setup_feature=cur_setup_feature_obj)

            feature_replacement[cur_scenario_device].add_remaining_setup_features_as_autonomous(cur_setup_device)

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
            raise KeyError("the requested setup device exists more than one time in `base_device_mapping`")
        return [cur_key for cur_key, cur_value in self.base_device_mapping.items() if cur_value == setup_device][0]

    def get_executor_for_testcase(self, testcase: callable) -> TestcaseExecutor | None:
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

    def cleanup_empty_executor_branches(self, consider_discarded=False):
        """
        This method searches the whole tree and removes branches where an executor item has no own children. It can
        remove these branches, because they have no valid matchings.

        This method implementation of the :class:`VariationExecutor` does nothing.
        """

    def update_scenario_device_feature_instances(self):
        """
        This method ensures that the (mostly abstract) feature instances of a scenario are exchanged with the
        feature instances of the assigned setup devices
        """
        for cur_scenario_device, cur_replacement_mapping in self.feature_replacement.items():
            for cur_feature_mapping in cur_replacement_mapping.mappings:
                setattr(cur_scenario_device, cur_feature_mapping.attr_name, cur_feature_mapping.setup_feature)

    def revert_scenario_device_feature_instances(self):
        """
        This method ensures that all initialized feature instances of a scenario are set back to the initial given
        features.
        """
        for cur_scenario_device, cur_replacement_mapping in self.feature_replacement.items():
            for cur_feature_mapping in cur_replacement_mapping.mappings:
                setattr(cur_scenario_device, cur_feature_mapping.attr_name, cur_feature_mapping.scenario_feature)

    def update_active_vdevice_device_mappings_in_all_features(self):
        """
        This method ensures that the correct `active_vdevices` property in all feature classes of the related setup and
        scenario-device classes are set correctly.
        """

        for cur_setup_device, feature_vdevice_mapping in self.abs_setup_feature_vdevice_mappings.items():
            if cur_setup_device not in self._original_active_vdevice_mappings.keys():
                self._original_active_vdevice_mappings[cur_setup_device] = FeatureVDeviceMapping()
            for cur_setup_feature in feature_vdevice_mapping.features:
                vdev_dev_mappings_of_setup_feat = feature_vdevice_mapping.get_mappings_for_feature(cur_setup_feature)

                cur_setup_feature_vdevice = vdev_dev_mappings_of_setup_feat[0].vdevice
                cur_mapped_setup_device = vdev_dev_mappings_of_setup_feat[0].device

                # first save old value to revert it later
                self._original_active_vdevice_mappings[cur_setup_device].add(
                    feature=cur_setup_feature,
                    mappings=cur_setup_feature.active_vdevices
                )
                # now set new value
                cur_setup_feature.active_vdevices = {cur_setup_feature_vdevice: cur_mapped_setup_device}

                # now also determine the mapping for the scenario-feature (if there exists one)
                cur_scenario_device = self.get_scenario_device_for(cur_setup_device)
                cur_scenario_feature = self.feature_replacement[cur_scenario_device].get_replaced_scenario_feature_for(
                    cur_setup_feature
                )
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
                            self._original_active_vdevice_mappings[cur_scenario_device] = FeatureVDeviceMapping()
                        # first save old value to revert it later
                        self._original_active_vdevice_mappings[cur_scenario_device].add(
                            feature=cur_scenario_feature,
                            mappings=cur_scenario_feature.active_vdevices
                        )
                        # now set new value
                        cur_scenario_feature.active_vdevices = \
                            {cur_scenario_feature_vdevice[0]: self.get_scenario_device_for(cur_mapped_setup_device)}

    def revert_active_vdevice_device_mappings_in_all_features(self):
        """
        This method ensures that the `active_vdevices` property that was changed with
        `update_active_vdevice_device_mappings_in_all_features()` will be reverted correctly.
        """
        for cur_feature_vdevice_mapping in self._original_active_vdevice_mappings.values():
            for cur_feature in cur_feature_vdevice_mapping.features:
                cur_original_mapping = {
                    mapping.vdevice:mapping.device
                    for mapping in cur_feature_vdevice_mapping.get_mappings_for_feature(cur_feature)
                }
                cur_feature.active_vdevices = cur_original_mapping

    def exchange_unmapped_vdevice_references(self):
        """
        This method exchanges all :class:`VDevice` references to an instance of :class:`UnmappedVDevice` if the
        :class:`VDevice` is not in an active VDevice-mapping.
        """
        all_devices = NormalScenarioSetupController.get_for(
            self.cur_scenario_class.__class__).get_all_abs_inner_device_classes()
        all_devices += NormalScenarioSetupController.get_for(
            self.cur_setup_class.__class__).get_all_abs_inner_device_classes()

        for cur_device in all_devices:
            cur_device_controller = DeviceController.get_for(cur_device)
            for _, cur_feature in cur_device_controller.get_all_instantiated_feature_objects().items():
                for cur_vdevice in FeatureController.get_for(cur_feature.__class__).get_abs_inner_vdevice_classes():
                    if cur_vdevice in cur_feature.active_vdevices.keys():
                        # do not exchange something, because this one is the active one
                        pass
                    else:
                        # set the `UnmappedVDevice` to this VDevice to ensure that it will not be accessed during this
                        # variation
                        setattr(cur_feature, cur_vdevice.__name__, UnmappedVDevice())

    def restore_original_vdevice_references(self):
        """
        This method restores all previously exchanged :class:`VDevice` references to the original ones.
        """
        all_devices = NormalScenarioSetupController.get_for(
            self.cur_scenario_class.__class__).get_all_abs_inner_device_classes()
        all_devices += NormalScenarioSetupController.get_for(
            self.cur_setup_class.__class__).get_all_abs_inner_device_classes()

        for cur_device in all_devices:
            cur_device_controller = DeviceController.get_for(cur_device)
            for _, cur_feature in cur_device_controller.get_all_instantiated_feature_objects().items():
                original_vdevices = FeatureController.get_for(cur_feature.__class__).get_original_vdevice_definitions()
                for cur_vdevice_name, cur_original_vdevice in original_vdevices.items():
                    setattr(cur_feature, cur_vdevice_name, cur_original_vdevice)

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
                    cur_vdevice_all_features = cur_vdevice_controller.get_all_instantiated_feature_objects()

                    cur_device_controller = DeviceController.get_for(cur_device)
                    cur_device_all_features = cur_device_controller.get_all_instantiated_feature_objects()
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

    def verify_applicability(self) -> None:
        """
        This method verifies if this variation is executable. First the method checks if all defined
        :class:`Feature` instances are available and fully implemented in the mapped setup :class:`Device`.
        Furthermore, it checks if their exists a valid routing which also matches the defined class `@for_vdevice`
        definition of the used :class:`Feature` classes.
        """
        self._applicability_check_done = True
        try:
            self.determine_feature_replacement_and_vdevice_mappings()

            self._verify_applicability_trough_feature_implementation_matching()

            self._verify_applicability_trough_vdevice_feature_impl_matching()

            self._verify_applicability_trough_all_valid_routings()
        except NotApplicableVariationException as not_applicable_variation_exc:
            # this variation can not be used, because the features can not be resolved correctly!
            self._not_applicable_variation_exc = not_applicable_variation_exc
            self.prev_mark = PreviousExecutorMark.DISCARDED

    def can_be_applied(self) -> bool:
        """
        :return: returns True if the previous verify_applicability check was successfully
        """
        if self._applicability_check_done is not True:
            raise RuntimeError('this method can not be used before no check was executed')

        return self._not_applicable_variation_exc is None

    def determine_absolute_scenario_device_connections(self):
        """
        This method determines the absolute connections for this variation and sets the internal properties
        `_abs_variation_*_device_connections` with them. This will be used to determine the real connection-subtree
        (that can be used for this variation) by the method `create_all_valid_routings()`.

        The method re-executes the algorithm to determine the absolute connections for a scenario/setup (see the method
        :meth:`Collector.determine_absolute_device_connections_for`), but it considers the real applied vDevice and
        their feature restrictions too.
        """
        # first determine all relevant absolute connection depending on the current scenario
        abs_var_scenario_device_cnns = self.cur_scenario_controller.get_all_abs_connections()

        # now iterate over every feature, that is used by the scenario and determine the class-based feature connections
        # of the mapped scenario feature (and its vDevice)
        for cur_setup_device, feature_vdev_mapping in self.abs_setup_feature_vdevice_mappings.items():
            cur_scenario_device = self.get_scenario_device_for(cur_setup_device)
            for cur_setup_feature, vdev_mappings_of_setup_feature in feature_vdev_mapping.items():
                cur_scenario_feature: Feature = (
                    self.feature_replacement[cur_scenario_device].get_replaced_scenario_feature_for(
                        setup_feature=cur_setup_feature)
                )

                if vdev_mappings_of_setup_feature[0].device not in self.base_device_mapping.values():
                    raise NotApplicableVariationException(
                        f'the mapped setup device `{vdev_mappings_of_setup_feature[0].device.__qualname__}` which is '
                        f'mapped to the VDevice `{vdev_mappings_of_setup_feature[0].vdevice.__qualname__}` is no part '
                        f'of this variation')

                cur_mapped_scenario_device = self.get_scenario_device_for(vdev_mappings_of_setup_feature[0].device)

                # get relevant class based connections for the current feature on setup level (this is really be used
                # here)
                feat_cnn = FeatureController.get_for(cur_setup_feature.__class__)\
                    .get_abs_class_based_for_vdevice()[vdev_mappings_of_setup_feature[0].vdevice]
                # connection that are relevant for this feature
                relevant_cnns = [
                    cnn for cnn in abs_var_scenario_device_cnns
                    if (cnn.has_connection_from_to(cur_scenario_device, end_device=cur_mapped_scenario_device)
                        and max(single_feat_cnn.contained_in(cnn, ignore_metadata=True)
                                for single_feat_cnn in feat_cnn.get_singles())
                        )
                ]

                if len(relevant_cnns) > 1:
                    raise UnclearAssignableFeatureConnectionError(
                        f"the devices {cur_scenario_device.__name__} and {cur_mapped_scenario_device.__name__} have "
                        f"multiple parallel connections - the device `{cur_scenario_device.__name__}` uses a feature "
                        f"`{cur_scenario_feature.__class__.__name__}` that matches with the device "
                        f"`{cur_mapped_scenario_device.__name__}`, but it is not clear which of the parallel "
                        f"connection could be used")

                if len(relevant_cnns) == 0:
                    # todo this does not map here
                    raise ValueError("can not find matching connection on scenario level")

                relevant_device_cnn = relevant_cnns[0]

                # now cleanup the scenario-device connection `relevant_device_cnn` according to the class-based feature
                # connection
                new_cnn_to_replace = Connection.based_on(OrConnectionRelation(*[
                    cur_old_cnn_single for cur_old_cnn_single in relevant_device_cnn.get_singles()
                    if feat_cnn.contained_in(cur_old_cnn_single, ignore_metadata=True)
                ]))
                new_cnn_to_replace.set_metadata_for_all_subitems(relevant_device_cnn.metadata)

                abs_var_scenario_device_cnns.remove(relevant_device_cnn)
                abs_var_scenario_device_cnns.append(new_cnn_to_replace)

                # we do not need to check other direction because `has_connection_from_to()` returns both possibilities

        # set the determined values in variation object
        self._abs_variation_scenario_device_connections = abs_var_scenario_device_cnns

    def create_all_valid_routings(self):
        """
        This method determines all valid routings for the current variation. It iterates over every defined
        absolute determined :class:`Connection` in the :class:`Scenario` class and trys to find a valid routing for it.

        .. note::
            The method assigns a full report with all valid routings into the local property `_routings`.
        """
        self._routings = {}
        for scenario_device, _ in self._base_device_mapping.items():
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
                    virtual_routing_cnns[cur_cnn] = Connection.based_on(virtual_cnn)
                else:
                    virtual_routing_cnns[cur_cnn] = Connection.based_on(
                        OrConnectionRelation(virtual_routing_cnns[cur_cnn], virtual_cnn))
                virtual_routing_cnns[cur_cnn].set_metadata_for_all_subitems(virtual_cnn.metadata)

        self._abs_variation_connections = []
        for cur_cnn in self._abs_variation_scenario_device_connections:
            cur_virtual_cnn = virtual_routing_cnns[cur_cnn]
            new_intersection = cur_cnn.intersection_with(cur_virtual_cnn)
            if new_intersection:
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
        for _, setup_device in self._base_device_mapping.items():
            setup_device_instantiated_features = \
                DeviceController.get_for(setup_device).get_all_instantiated_feature_objects()
            for _, cur_setup_feature in setup_device_instantiated_features.items():

                cur_setup_feature_controller = FeatureController.get_for(cur_setup_feature.__class__)
                method_var_data_of_feature = cur_setup_feature_controller.get_method_based_for_vdevice()
                if method_var_data_of_feature is None:
                    # ignore if no method-variations exists for the current feature
                    continue

                method_var_selection = {}

                for cur_method_name, _ in inspect.getmembers(
                        cur_setup_feature, lambda o: inspect.isfunction(o) or inspect.ismethod(o)):

                    if cur_method_name not in method_var_data_of_feature.keys():
                        # ignore if there was no method-variation registration for the current method
                        continue

                    mapped_vdevice, mapped_setup_device = cur_setup_feature.active_vdevice_device_mapping
                    # get all absolute connections for this setup device
                    relevant_abs_conn = []
                    for cur_cnn in self._abs_variation_connections:
                        if cur_cnn.has_connection_from_to(start_device=setup_device, end_device=mapped_setup_device):
                            # add the children
                            relevant_abs_conn.extend(
                                cur_cnn.based_on_elements.connections if cur_cnn.__class__ == Connection else [cur_cnn]
                            )

                    if len(relevant_abs_conn) is None:
                        raise RuntimeError(f"detect empty absolute connection between device `{setup_device.__name__}` "
                                           f"and device `{mapped_setup_device.__name__}`")
                    absolute_feature_method_var_cnn = Connection.based_on(OrConnectionRelation(*relevant_abs_conn))
                    cur_method_variation = cur_setup_feature_controller.get_method_variation(
                        of_method_name=cur_method_name, for_vdevice=mapped_vdevice,
                        with_connection=absolute_feature_method_var_cnn)
                    if cur_method_variation is None:
                        raise AttributeError(f"can not find a valid method variation for method `{cur_method_name}` "
                                             f"of feature `{cur_setup_feature.__class__.__name__}`")
                    method_var_selection[cur_method_name] = \
                        (mapped_vdevice, absolute_feature_method_var_cnn, cur_method_variation)

                cur_setup_feature_controller.set_active_method_variation(method_selection=method_var_selection)

    def resolve_and_exchange_unresolved_parametrization(self):
        """resolves the parametrization if there are any :class:`UnresolvedParametrizedTestcaseExecutor` in the tree"""
        replaced_executors = []
        for cur_child in self._testcase_executors:
            if isinstance(cur_child, UnresolvedParametrizedTestcaseExecutor):
                replaced_executors.extend(cur_child.get_resolved_parametrized_testcase_executors())
            else:
                replaced_executors.append(cur_child)
        self._testcase_executors = replaced_executors
