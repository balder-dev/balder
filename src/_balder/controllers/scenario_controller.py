from __future__ import annotations
from typing import Type, Dict, List, Tuple, Union, Callable, Iterable, Any

import logging
import inspect
from collections import OrderedDict
from _balder.cnnrelations import OrConnectionRelation
from _balder.device import Device
from _balder.scenario import Scenario
from _balder.connection import Connection
from _balder.controllers.feature_controller import FeatureController
from _balder.controllers.device_controller import DeviceController
from _balder.controllers.normal_scenario_setup_controller import NormalScenarioSetupController
from _balder.parametrization import FeatureAccessSelector, Parameter
from _balder.exceptions import UnclearAssignableFeatureConnectionError, ConnectionIntersectionError, \
    MultiInheritanceError
from _balder.utils.functions import get_scenario_inheritance_list_of

logger = logging.getLogger(__file__)


class ScenarioController(NormalScenarioSetupController):
    """
    This is the controller class for :class:`Scenario` items.
    """

    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing scenarios and its corresponding controller object
    _items: Dict[Type[Scenario], ScenarioController] = {}

    _parametrization: Dict[Callable, Dict[str, Union[Iterable[Any], FeatureAccessSelector]]] = {}

    def __init__(self, related_cls, _priv_instantiate_key):

        # describes if the current controller is for setups or for scenarios (has to be set in child controller)
        self._related_type = Scenario

        # holds covered-by configuration
        self._covered_by = {}

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

    def register_parametrization(
            self,
            test_method: Callable,
            field_name: str,
            values: Iterable[Any] | FeatureAccessSelector
    ) -> None:
        """
        This method registers a custom parametrization for a test method of this Scenario
        """
        if test_method not in self.get_all_test_methods():
            raise ValueError(f'got test method `{test_method.__qualname__}` which is no part of the '
                             f'scenario `{self.related_cls}`')
        if test_method not in self._parametrization.keys():
            self._parametrization[test_method] = {}
        if field_name in self._parametrization[test_method].keys():
            raise ValueError(f'field name `{field_name}` for test method `{test_method.__qualname__}` already '
                             f'registered')
        self._parametrization[test_method][field_name] = values

    def get_parametrization_for(
            self,
            test_method: Callable,
            static: bool = True,
            dynamic: bool = True,
    ) -> OrderedDict[str, Iterable[Any] | FeatureAccessSelector] | None:
        """
        This method returns the parametrization for a test method of this Scenario. It returns the parameter
        configuration for every parameter in an OrderedDict.

        :param test_method: the test method of the Scenario
        :param static: if False, all static parameters will not be included into the dict.
        :param dynamic: if False, all dynamic parameters will not be included into the dict.
        """
        if test_method not in self._parametrization.keys():
            return None
        params = self._parametrization[test_method]

        # get arguments in defined order
        arguments = [name for name in inspect.getfullargspec(test_method).args if name in params.keys()]
        ordered_dict = OrderedDict()
        for cur_arg in arguments:
            cur_value = params[cur_arg]
            if isinstance(cur_value, FeatureAccessSelector) and dynamic is False:
                continue
            if not isinstance(cur_value, FeatureAccessSelector) and static is False:
                continue
            ordered_dict[cur_arg] = params[cur_arg]
        return ordered_dict

    def register_covered_by_for(self, meth: Union[str, None], covered_by: Union[Scenario, Callable, None]) -> None:
        """
        This method registers a covered-by statement for this Scenario. If `meth` is provided, the statement is for the
        specific test method of the scenario, otherwise it is for the whole setup. The item provided in `covered_by`
        describes the test object that covers this scenario (method).

        :param meth: if provided this attribute describes the test method that should be registered, otherwise the whole
                     scenario will be registered
        :param covered_by: describes the test object that covers this scenario (method)
        """
        if not (meth is None or isinstance(meth, str)):
            raise TypeError('meth needs to be None or a string')
        if meth is not None:
            if not meth.startswith('test_'):
                raise TypeError(
                    f"the use of the `@covered_by` decorator is only allowed for `Scenario` objects and test methods "
                    f"of `Scenario` objects - the method `{self.related_cls.__name__}.{meth}` does not start with "
                    f"`test_` and is not a valid test method")
            if not hasattr(self.related_cls, meth):
                raise ValueError(
                    f"the provided test method `{meth}` does not exist in scenario `{self.related_cls.__name__}`"
                )

        if meth not in self._covered_by.keys():
            self._covered_by[meth] = []
        if covered_by is None:
            # reset it
            # todo what if there are more than one decorator in one class
            del self._covered_by[meth]
        else:
            self._covered_by[meth].append(covered_by)

    def get_raw_covered_by_dict(self) -> Dict[Union[str, None], List[Union[Scenario, Callable]]]:
        """
        :return: returns the internal covered-by dictionary
        """
        return self._covered_by.copy()

    def get_abs_covered_by_dict(self) -> Dict[Union[str, None], List[Union[Scenario, Callable]]]:
        """
        This method resolves the covered-by statements over all inheritance levels. It automatically
        cleans up every inheritance of the covered_by decorators for every parent class of this scenario.
        """
        parent_classes = [p for p in self.related_cls.__bases__ if issubclass(p, Scenario) and p != Scenario]
        if len(parent_classes) > 1:
            raise MultiInheritanceError(
                f'can not resolve classes for `{self.related_cls}` because there are more than one Scenario based '
                f'parent classes'
            )
        # no more parent classes -> raw is absolute
        if len(parent_classes) == 0:
            return self.get_raw_covered_by_dict()
        parent_controller = self.__class__.get_for(parent_classes[0])
        self_raw_covered_by_dict = self.get_raw_covered_by_dict()

        #: first fill result with data from parent controller
        result = {
            k if k is None else getattr(self.related_cls, k.__name__): v
            for k, v in parent_controller.get_abs_covered_by_dict().items()
        }
        for cur_callable, cur_coveredby in self_raw_covered_by_dict.items():
            if cur_callable in result.keys():
                result[cur_callable].extend(cur_coveredby)
            else:
                result[cur_callable] = cur_coveredby
        return result

    def check_for_parameter_loop_in_dynamic_parametrization(self, cur_fn: Callable):
        """
        This method checks for a parameter loop in all dynamic parametrization for a specific test method. If it detects
        a loop an AttributeError is thrown
        """
        # only dynamic parametrization can have Parameter
        parametrization = self.get_parametrization_for(cur_fn, static=False, dynamic=True)

        def get_dependent_parameters_of_attribute(attribute: str) -> List[str] | None:
            cur_feature_access_selector = parametrization.get(attribute)
            if cur_feature_access_selector is None:
                return None
            # relevant are parameters only if they are from :class:`Parameter` and contained in the dynamic
            # parametrization
            return [param.name for param in cur_feature_access_selector.parameters.values()
                    if isinstance(param, Parameter) and param.name in parametrization.keys()]

        def recursive_parameter_loop_check(for_attribute, with_attribute: str):
            dependent_attr = get_dependent_parameters_of_attribute(with_attribute)
            if dependent_attr is None:
                # no problematic dependencies because attribute is no dynamic attribute
                return
            if len(dependent_attr) == 0:
                # no problematic dependencies
                return

            if for_attribute in dependent_attr:
                # loop detected
                raise AttributeError('detect a loop in Parameter() object - can not apply parametrization')
            # go deeper and resolve all dependent
            for cur_dependent_attr in dependent_attr:
                recursive_parameter_loop_check(for_attribute, cur_dependent_attr)
            return

        for cur_attr in parametrization.keys():
            recursive_parameter_loop_check(cur_attr, cur_attr)

    def get_next_parent_class(self) -> Union[Type[Scenario], None]:
        """
        This method returns the next parent class which is a subclass of the :class:`Scenario` itself.

        :return: returns the next parent class or None if the next parent class is :class:`Scenario`
                 itself
        """
        next_base_class = None
        for cur_base in self.related_cls.__bases__:
            if issubclass(cur_base, Scenario):
                if next_base_class is not None:
                    raise MultiInheritanceError(
                        f"found more than one Scenario parent classes for `{self.related_cls.__name__}` "
                        f"- multi inheritance is not allowed for Scenario/Setup classes")
                next_base_class = cur_base
        if next_base_class == Scenario:
            return None
        return next_base_class

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

    def get_ignore_test_methods(self) -> List[callable]:
        """
        This method returns a list of all methods that have the IGNORE marker. It automatically resolves marker that
        were provided on parent class scenarios.
        """
        result = []
        next_parent_class = get_scenario_inheritance_list_of(self.related_cls)[1]
        if next_parent_class != Scenario:
            next_parent_class_controller = ScenarioController.get_for(next_parent_class)
            next_parent_ignore_meths = next_parent_class_controller.get_ignore_test_methods()
            result.extend(next_parent_ignore_meths)
        for cur_ignore_meth_as_str in self.related_cls.IGNORE:
            cur_ignore_meth = getattr(self.related_cls, cur_ignore_meth_as_str)
            result.append(cur_ignore_meth)
        return list(set(result))

    def get_skip_test_methods(self) -> List[callable]:
        """
        This method returns a list of all methods that have the SKIP marker. It automatically resolves marker that were
        provided on parent class scenarios.
        """
        result = []
        next_parent_class = get_scenario_inheritance_list_of(self.related_cls)[1]
        next_parent_ignore_meths = []

        if next_parent_class != Scenario:
            next_parent_class_controller = ScenarioController.get_for(next_parent_class)
            next_parent_ignore_meths = next_parent_class_controller.get_ignore_test_methods()
            next_parent_skip_meths = next_parent_class_controller.get_skip_test_methods()
            result.extend(next_parent_skip_meths)

        for cur_skip_meth_as_str in self.related_cls.SKIP:
            cur_skip_meth = getattr(self.related_cls, cur_skip_meth_as_str)
            if cur_skip_meth in next_parent_ignore_meths:
                raise ValueError(f'found skip method `{cur_skip_meth}` defined in `{self.related_cls}.SKIP`, but was '
                                 f'already added to IGNORE in parent class')
            result.append(cur_skip_meth)

        return list(set(result))

    def get_run_test_methods(self) -> List[callable]:
        """
        This method returns a list of all methods that should run in this scenario. It automatically resolves
        SKIP/IGNORE marker that were provided on parent class scenarios.
        """
        result = (set(self.get_all_test_methods())
                  - set(self.get_skip_test_methods())
                  - set(self.get_ignore_test_methods()))
        return list(result)

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
                feature_cnn = FeatureController.get_for(
                    cur_feature.__class__).get_abs_class_based_for_vdevice()[mapped_vdevice]

                # search node names that is the relevant connection
                relevant_cnns: List[Connection] = []
                mapped_device_abs_cnns = DeviceController.get_for(mapped_device).get_all_absolute_connections()
                for _, all_connections in mapped_device_abs_cnns.items():
                    relevant_cnns += [cur_cnn for cur_cnn in all_connections
                                      if cur_cnn.has_connection_from_to(cur_from_device, end_device=mapped_device)]

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

        def reduce_based_on_feature_cnns_for_devices(
                feature_cnn: Connection, dev1: Type[Device], node_dev1: str, dev2: Type[Device], node_dev2: str):
            # execute further process only if there is exactly one relevant connection
            start_length_before_reduction = \
                len(all_abs_single_connections[dev1][node_dev1][
                        dev2][node_dev2])
            for cur_abs_connection in \
                    all_abs_single_connections[dev1][node_dev1][
                        dev2][node_dev2].copy():
                if not feature_cnn.contained_in(cur_abs_connection, ignore_metadata=True):
                    # this abs single connection is not fulfilled by the current feature -> remove it
                    all_abs_single_connections[dev1][node_dev1][
                        dev2][node_dev2].remove(cur_abs_connection)
                    add_reduction_candidate(dev1, dev2, cur_abs_connection)
            if start_length_before_reduction > 0 and \
                    len(all_abs_single_connections[dev1][node_dev1][
                            dev2][node_dev2]) == 0:
                raise ConnectionIntersectionError(
                    f"the `{self.related_cls.__name__}` has a connection from device "
                    f"`{dev1.__name__}` to `{dev2.__name__}` - some mapped VDevices of "
                    f"their feature classes define mismatched connections")

        def get_single_cnns_between_device_for_feature(from_device, to_device, relevant_feature_cnn):
            # search node names that is the relevant connection
            relevant_cnns: List[List[Connection]] = []
            for _, cur_node_data in all_abs_single_connections[from_device].items():
                for cur_to_device, cur_to_device_data in cur_node_data.items():
                    if cur_to_device == to_device:
                        relevant_cnns += [cur_cnns for _, cur_cnns in cur_to_device_data.items()]

            result_singles = None
            if len(relevant_cnns) > 1:
                # there exists parallel connections - filter only the relevant one
                for cur_single_cnns in relevant_cnns:
                    for cur_single_cnn in cur_single_cnns:
                        if relevant_feature_cnn.contained_in(cur_single_cnn):
                            # this is the relevant connection (all other can not fit, because we have
                            # already checked this with method
                            # `scenario_controller.validate_feature_clearance_for_parallel_connections()`)
                            result_singles = cur_single_cnns
                            break
                    if result_singles is not None:
                        break
            elif len(relevant_cnns) == 1:
                result_singles = relevant_cnns[0]
            if result_singles is None:
                raise ValueError("can not find relevant connection of all parallel connections")
            return result_singles

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
                cur_feature_cnn = \
                    FeatureController.get_for(
                        cur_feature.__class__).get_abs_class_based_for_vdevice()[mapped_vdevice]

                device_cnn_singles = get_single_cnns_between_device_for_feature(
                    from_device=cur_from_device, to_device=mapped_device, relevant_feature_cnn=cur_feature_cnn)

                reduce_based_on_feature_cnns_for_devices(
                    cur_feature_cnn, device_cnn_singles[0].from_device, device_cnn_singles[0].from_node_name,
                    device_cnn_singles[0].to_device, device_cnn_singles[0].to_node_name)
                # do the same for the opposite direction (features are always bidirectional)
                reduce_based_on_feature_cnns_for_devices(
                    cur_feature_cnn, device_cnn_singles[0].to_device, device_cnn_singles[0].to_node_name,
                    device_cnn_singles[0].from_device, device_cnn_singles[0].from_node_name)

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

                        new_cnn = Connection.based_on(OrConnectionRelation(*cur_single_cnns))
                        new_cnn.set_metadata_for_all_subitems(cur_single_cnns[0].metadata)
                        if cur_from_device == cur_single_cnns[0].from_device:
                            cur_from_device_controller.add_new_absolute_connection(new_cnn)
                        else:
                            cur_to_device_controller.add_new_absolute_connection(new_cnn)
