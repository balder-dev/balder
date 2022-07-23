from __future__ import annotations

import logging
from typing import List, Type, Union, Dict, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.plugin_manager import PluginManager

import os
import sys
import types
import inspect
import pathlib
import functools
import importlib.util
from _balder.utils import inspect_method, get_class_that_defines_method
from _balder.setup import Setup
from _balder.device import Device
from _balder.feature import Feature
from _balder.vdevice import VDevice
from _balder.scenario import Scenario
from _balder.connection import Connection
from _balder.controllers import ScenarioController, SetupController, DeviceController, VDeviceController, \
    FeatureController
from _balder.exceptions import InnerFeatureResolvingError, VDeviceResolvingError, IllegalVDeviceMappingError, \
    DeviceResolvingException, UnclearAssignableFeatureConnectionError, ConnectionIntersectionError, \
    DuplicateForVDeviceError, UnknownVDeviceException, DeviceOverwritingError, MultiInheritanceError, \
    FeatureOverwritingError, VDeviceOverwritingError
from _balder.utils import get_scenario_inheritance_list_of

logger = logging.getLogger(__file__)


class Collector:
    """
    The Collector class manages the loading and importing of all relevant balder objects. It does not resolve something,
    but secures that all relevant data is being collected.
    """

    # this static attribute will be managed by the decorator `@for_vdevice(..)`. It holds all functions/methods that
    # were decorated with `@for_vdevice(..)` (without checking their correctness). The collector will check them later
    # with the method `rework_method_variation_decorators()`
    _possible_method_variations: Dict[
        Callable,
        List[Tuple[Union[Type[VDevice], str],
                   Union[Type[Connection], Connection, Tuple[Union[Type[Connection], Connection]],
                         List[Union[Type[Connection], Connection, Tuple[Union[Type[Connection], Connection]]]]]]]] = {}

    def __init__(self, working_dir: pathlib.Path):
        self.working_dir = pathlib.Path(working_dir)

        # add the working directory to the official python path
        sys.path.insert(0, str(self.working_dir.parent.absolute()))

        self._all_py_files: Union[List[Type[pathlib.Path]], None] = None
        self._all_scenarios: Union[List[Type[Scenario]], None] = None
        self._all_setups: Union[List[Type[Setup]], None] = None
        self._all_connections: Union[List[Type[Connection]], None] = None

        self.balderglob_was_loaded = False

    @property
    def all_pyfiles(self) -> List[Type[pathlib.Path]]:
        if self._all_py_files is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_py_files

    @property
    def all_scenarios(self) -> List[Type[Scenario]]:
        if self._all_scenarios is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_scenarios

    @property
    def all_setups(self) -> List[Type[Setup]]:
        if self._all_setups is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_setups

    @property
    def all_connections(self) -> List[Type[Connection]]:
        if self._all_connections is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_connections

    def load_balderglob_py_file(self) -> Union[types.ModuleType, None]:
        """
        This method loads the global balderglob.py file and returns the module or None if the file does not exist.
        """
        filepath = self.working_dir.joinpath('balderglob.py')

        module_name = "{}.balderglob".format(self.working_dir.stem)

        if self.balderglob_was_loaded:
            return sys.modules[module_name]

        if filepath.is_file():
            self.balderglob_was_loaded = True

            spec = importlib.util.spec_from_file_location(module_name, filepath)
            cur_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = cur_module
            spec.loader.exec_module(cur_module)
            return cur_module
        return None

    def get_all_py_files(self) -> List[pathlib.Path]:
        """
        This method returns all python modules that the system can find in the current set WORKING_DIR. It doesn't
        matter what kind of modules it is or what content they offer.
        """
        all_paths: List[pathlib.Path] = []

        for root, dirs, files in os.walk(str(self.working_dir)):
            for file in files:
                if file.endswith(".py"):
                    all_paths.append(pathlib.Path(os.path.join(root, file)))
        return all_paths

    def get_all_scenario_classes(self, py_file_paths: List[pathlib.Path], filter_abstracts: bool = True) -> \
            List[Type[Scenario]]:
        """
        This method searches all py-file paths that are given with the parameter ``py_file_paths``. It searches for all
        valid balder :class:`Scenario` classes. First the method filters the paths for the files that begin with
        ``scenario_*`` and then searches in the file for classes that begin with ``Scenario*``. Afterwards, it checks
        that the class is a subclass from :class:`Scenario`.

        :param py_file_paths: a list of python files the collector should search through to extract the
                              :meth:`Scenario` classes

        :param filter_abstracts: if this value is True, abstract :meth:`Scenario` classes will be filtered

        :return: a list of all classes (subclasses of :meth:`Scenario`) that are found by the method in the given
                 file paths
        """
        result = []
        for cur_path in py_file_paths:
            #: only use files that match the filter
            if cur_path.parts[-1].startswith('scenario_'):
                module_name = "{}.{}.{}".format(
                    self.working_dir.stem, ".".join(cur_path.parent.relative_to(self.working_dir).parts), cur_path.stem)
                if module_name not in sys.modules.keys():
                    spec = importlib.util.spec_from_file_location(module_name, cur_path)
                    cur_module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = cur_module
                    spec.loader.exec_module(cur_module)
                    class_members = inspect.getmembers(cur_module, inspect.isclass)
                    for cur_class_name, cur_class in class_members:
                        if cur_class_name.startswith('Scenario') and issubclass(cur_class, Scenario) \
                                and cur_class != Scenario:
                            if filter_abstracts and inspect.isabstract(cur_class):
                                break
                            if cur_class not in result:
                                result.append(cur_class)
        return result

    def load_all_connection_classes(self, py_file_paths: List[pathlib.Path]) -> None:
        """
        This method searches all py-file paths that are given with the parameter ``py_file_paths``. It searches for all
        valid balder :class:`Connection` classes. The method imports all classes that are directly located in a
        submodule `connections` (py file or package directory).

        :param py_file_paths: a list of python files that the collector should search through to extract the
                              :meth:`Connection` classes

        :return: a list of all classes (subclasses of :meth:`Connection`) that are found by the method in the
                 given files
        """
        for cur_path in py_file_paths:
            #: only use files that match the filter
            if 'connections' in cur_path.parts[-2] or 'connections.py' == cur_path.parts[-1]:
                module_name = "{}.{}.{}".format(
                    self.working_dir.stem, ".".join(cur_path.parent.relative_to(self.working_dir).parts), cur_path.stem)
                spec = importlib.util.spec_from_file_location(module_name, cur_path)
                cur_module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = cur_module
                spec.loader.exec_module(cur_module)

    def get_all_connection_classes(self) -> List[Type[Connection]]:
        """
        The method determines all available classes that are inherited from the base class :meth:`Connection`.

        :return: a list of all classes (subclasses of :meth:`Connection`) that are found in all imported modules
        """
        result = []
        modules = sys.modules.copy()
        for cur_module_name, cur_module in modules.items():
            try:
                for _, cur_class in inspect.getmembers(cur_module, inspect.isclass):
                    if issubclass(cur_class, Connection) and cur_class not in result:
                        result.append(cur_class)
            except ModuleNotFoundError:
                # skip these errors if some modules has wrong module references
                pass
        return result

    def get_all_setup_classes(self, py_file_paths: List[pathlib.Path], filter_abstracts: bool = True) -> \
            List[Type[Setup]]:
        """
        This method searches all py-file paths that are given with the parameter ``py_file_paths``. It searches for all
        valid balder :class:`Setup` classes. First the method filters the paths for the files that begin with
        ``setup_*`` and then searches in the file for classes that begin with ``Setup*``. Afterwards, it checks
        that the class is a subclass from :class:`Setup`.

        :param py_file_paths: a list of python files the collector should search through to extract the
                              :meth:`Setup` classes

        :param filter_abstracts: if this value is True, abstract :meth:`Setup` classes will be filtered

        :return: a list of all classes (subclasses of :class:`Setup`) that are found by the method in the given
                 file paths
        """
        result = []
        for cur_path in py_file_paths:
            #: only use files that match the filter
            if cur_path.parts[-1].startswith('setup_'):
                module_name = "{}.{}.{}".format(
                    self.working_dir.stem, ".".join(cur_path.parent.relative_to(self.working_dir).parts), cur_path.stem)
                if module_name not in sys.modules.keys():
                    spec = importlib.util.spec_from_file_location(module_name, cur_path)
                    cur_module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = cur_module
                    spec.loader.exec_module(cur_module)
                    class_members = inspect.getmembers(cur_module, inspect.isclass)
                    for cur_class_name, cur_class in class_members:
                        if cur_class_name.startswith('Setup') and issubclass(cur_class, Setup) and cur_class != Setup:
                            if filter_abstracts and inspect.isabstract(cur_class):
                                break
                            if cur_class not in result:
                                result.append(cur_class)
        return result

    @staticmethod
    def filter_parent_classes_of(items: List[Union[Type[Scenario], Type[Setup]]]):
        """
        This method removes all parent classes from the given items. All items that also have children, will be removed
        from the returned list.
        """
        result = []
        for cur_class in items:
            a_child_class_exists = False
            for cur_other_class in items:
                if cur_class == cur_other_class:
                    # the current class is the class itself
                    continue
                if issubclass(cur_other_class, cur_class):
                    a_child_class_exists = True
                    break
            if not a_child_class_exists:
                result.append(cur_class)
        return result

    def set_original_device_features_for(self, scenarios_or_setups):
        """
        This method sets the important property `Device.__original_instanced_features` to ensure that the device
        retains an original representation of its abstract features. The real features are overwritten for each new
        variation by the :class:`ExecutorTree`!
        """
        for cur_scenario_or_setup in scenarios_or_setups:
            cur_scenario_or_setup_controller = None
            if issubclass(cur_scenario_or_setup, Scenario):
                cur_scenario_or_setup_controller = ScenarioController.get_for(cur_scenario_or_setup)
            elif issubclass(cur_scenario_or_setup, Setup):
                cur_scenario_or_setup_controller = SetupController.get_for(cur_scenario_or_setup)

            devices = cur_scenario_or_setup_controller.get_all_abs_inner_device_classes()
            for cur_device in devices:
                cur_device_controller = DeviceController.get_for(cur_device)
                new_originals = cur_device_controller.get_all_instantiated_feature_objects()
                if cur_device_controller.get_original_instanced_feature_objects():
                    if cur_device_controller.get_original_instanced_feature_objects() != new_originals:
                        raise EnvironmentError(
                            f"the device `{cur_device.__name__}` already has a static attribute value in "
                            f"`Device.__original_instanced_features`")

                cur_device_controller.set_original_instanced_feature_objects(new_originals)

    @staticmethod
    def validate_inheritance_of(items: List[Union[Type[Setup], Type[Scenario]]]):
        """
        This method validates that the inheritance of `Setup`/`Scenario` classes were being done correctly. It checks
        that all devices that are inherited has the same naming as their parents and also that every reused name (that
        is already be used for a device in parent class) does also inherit from the parent scenario/setup device.

        In addition to that, the method checks that either every device of higher class is defined (and overwritten) in
        the current class or non device
        """
        for cur_scenario_or_setup in items:
            cur_scenario_or_setup_controller = None
            if issubclass(cur_scenario_or_setup, Scenario):
                cur_scenario_or_setup_controller = ScenarioController.get_for(cur_scenario_or_setup)
            elif issubclass(cur_scenario_or_setup, Setup):
                cur_scenario_or_setup_controller = SetupController.get_for(cur_scenario_or_setup)

            parent_scenario_or_setup = None
            for cur_base_class in cur_scenario_or_setup.__bases__:
                if issubclass(cur_base_class, Scenario) or issubclass(cur_base_class, Setup):
                    if parent_scenario_or_setup is not None:
                        # multi inheritance is not allowed
                        raise MultiInheritanceError(
                            f"found more than one Scenario/Setup parent classes for `{cur_scenario_or_setup.__name__}` "
                            f"- multi inheritance is not allowed for Scenario/Setup classes")
                    parent_scenario_or_setup = cur_base_class
            if parent_scenario_or_setup == Scenario or parent_scenario_or_setup == Setup:
                # done, because the parent class is direct Scenario/Setup class
                continue

            parent_scenario_or_setup_controller = None
            if issubclass(parent_scenario_or_setup, Scenario):
                parent_scenario_or_setup_controller = ScenarioController.get_for(parent_scenario_or_setup)
            elif issubclass(parent_scenario_or_setup, Setup):
                parent_scenario_or_setup_controller = SetupController.get_for(parent_scenario_or_setup)

            devices = cur_scenario_or_setup_controller.get_all_inner_device_classes()
            abs_parent_devices = parent_scenario_or_setup_controller.get_all_abs_inner_device_classes()
            abs_parent_devices_as_names = [cur_parent.__name__ for cur_parent in abs_parent_devices]

            if len(devices) == 0:
                # ignore it because cur item has no special definitions
                pass
            else:
                # check if a device has the same name and/or inherits from a device of the parent item
                for cur_item_device in devices:
                    # check if name exist
                    relevant_parent_device_naming = None
                    if cur_item_device.__name__ in abs_parent_devices_as_names:
                        relevant_parent_device_naming = \
                            abs_parent_devices[abs_parent_devices_as_names.index(cur_item_device.__name__)]

                    # check if device is inherited
                    relevant_parent_device_inheritance = None
                    for cur_parent in abs_parent_devices:
                        if issubclass(cur_item_device, cur_parent):
                            if relevant_parent_device_inheritance is not None:
                                # multi inheritance is not allowed
                                raise MultiInheritanceError(
                                    f"found more than one Scenario/Setup Device parent classes for "
                                    f"`{cur_item_device.__name__}` - multi inheritance is not allowed for Device "
                                    f"classes")
                            relevant_parent_device_inheritance = cur_parent

                    # now check if both is fulfilled
                    if relevant_parent_device_naming == relevant_parent_device_inheritance and \
                            relevant_parent_device_inheritance is not None:
                        #
                        pass
                    elif relevant_parent_device_naming is None and relevant_parent_device_inheritance is None:
                        # both are none -> it is a new device -> ALLOWED
                        pass
                    elif relevant_parent_device_naming is None:
                        # reused a naming but does not inherit from it -> NOT ALLOWED
                        raise DeviceOverwritingError(
                            f"the inner device class `{cur_item_device.__qualname__}` which inherits from another "
                            f"device `{relevant_parent_device_inheritance.__qualname__}` - it should also have the "
                            f"same name")
                    elif relevant_parent_device_inheritance is None:
                        # inherit from a parent device, but it has not the same naming -> NOT ALLOWED
                        raise DeviceOverwritingError(
                            f"the inner device class `{cur_item_device.__qualname__}` has the same name than the "
                            f"device `{relevant_parent_device_naming.__qualname__}` - it should also inherit from it")

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
                            f"not implemented in child class `{cur_scenario_or_setup.__name__}`")

            # also check the parent class here
            Collector.validate_inheritance_of([parent_scenario_or_setup])

    @staticmethod
    def resolve_raw_fixtures():
        """
        This method resolves all raw fixtures and sets the resolved attribute `ExecutorTree.fixtures`
        """
        from .executor.executor_tree import ExecutorTree
        resolved_dict = {}
        for cur_level, cur_module_fixture_dict in ExecutorTree.raw_fixtures.items():
            resolved_dict[cur_level] = {}
            for cur_fn in cur_module_fixture_dict:
                cls, func_type = inspect_method(cur_fn)
                # mechanism also works for balderglob fixtures (`func_type` is 'function' and `cls` is None)
                if cls not in resolved_dict[cur_level].keys():
                    resolved_dict[cur_level][cls] = []
                resolved_dict[cur_level][cls].append((func_type, cur_fn))
        ExecutorTree.fixtures = resolved_dict

    def set_run_skip_ignore_of_test_methods_in_scenarios(self):
        """
        This method secures that the scenario classes have a valid RUN, SKIP and IGNORE attribute.
        """
        for cur_scenario in self._all_scenarios:
            # determines hierarchy of inherited classes
            base_classes = get_scenario_inheritance_list_of(cur_scenario)
            # removes the last scenario class
            base_classes = base_classes[:-1]
            # now determine all RUN, SKIP and IGNORE values if they aren't already mentioned - if there exists a value
            #  for them, check if the value is valid
            base_classes.reverse()
            for cur_idx in range(0, len(base_classes)):
                next_parent = None if cur_idx == 0 else base_classes[cur_idx - 1]
                cur_class = base_classes[cur_idx]
                if "IGNORE" in cur_class.__dict__.keys():
                    # IGNORE is mentioned in this specific class
                    if not isinstance(cur_class.IGNORE, list):
                        raise TypeError(
                            "the class attribute `{}.IGNORE` has to be from type list".format(cur_class.__name__))
                    # check that all elements that are mentioned here exists in the parent's RUN, SKIP or IGNORE class
                    # variable or are defined in this class
                    for cur_ignore_method in cur_class.IGNORE:
                        if not inspect.ismethod(cur_ignore_method) or \
                                not cur_ignore_method.__name__.startswith('test_'):
                            raise TypeError(
                                "the given element {} for class attribute `{}.IGNORE` is no valid test method".format(
                                    cur_ignore_method.__name__, cur_class.__name__))
                        if cur_ignore_method not in cur_class.__dict__.values() and next_parent is None or \
                                cur_ignore_method not in cur_class.__dict__.values() and next_parent is not None \
                                and cur_ignore_method not in next_parent.RUN \
                                and cur_ignore_method not in next_parent.SKIP \
                                and cur_ignore_method not in next_parent.IGNORE:
                            raise ValueError(
                                "the element `{}` given at class attribute `{}.IGNORE` is not a test method of this "
                                "scenario".format(cur_ignore_method.__name__, cur_class.__name__))
                else:
                    # IGNORE is not mentioned in this specific class -> so add an empty list for further access
                    cur_class.IGNORE = []
                if "SKIP" in cur_class.__dict__.keys():
                    # SKIP is mentioned in this specific class
                    if not isinstance(cur_class.SKIP, list):
                        raise TypeError(
                            "the class attribute `{}.SKIP` has to be from type list".format(cur_class.__name__))
                    # check that all elements that are mentioned here exist in the parent's RUN or SKIP class variable
                    # or are defined in this class
                    for cur_skip_method in cur_class.SKIP:
                        if not inspect.ismethod(cur_skip_method) or \
                                not cur_skip_method.__name__.startswith('test_'):
                            raise TypeError(
                                "the given element {} for class attribute `{}.IGNORE` is no valid test method".format(
                                    cur_skip_method.__name__, cur_class.__name__))
                        if cur_skip_method not in cur_class.__dict__.values():
                            if next_parent is None:
                                raise ValueError(
                                    "the element `{}` given at class attribute `{}.SKIP` is not a test method of this "
                                    "scenario".format(cur_skip_method.__name__, cur_class.__name__))
                            else:
                                if cur_skip_method in next_parent.IGNORE:
                                    raise ValueError(
                                        "the element `{}` given at class attribute `{}.SKIP` was already added to "
                                        "IGNORE in a higher parent class - not possible to add it now to SKIP".format(
                                            cur_skip_method.__name__, cur_class.__name__))
                                elif cur_skip_method not in next_parent.SKIP \
                                        and cur_skip_method not in next_parent.IGNORE:
                                    raise ValueError(
                                        "the element `{}` given at class attribute `{}.SKIP` is not a test method of "
                                        "this scenario".format(cur_skip_method.__name__, cur_class.__name__))
                else:
                    # SKIP is not mentioned in this specific class -> so add an empty list for further access
                    cur_class.SKIP = []
                if "RUN" in cur_class.__dict__.keys():
                    # RUN is mentioned in this specific class
                    if not isinstance(cur_class.RUN, list):
                        raise TypeError(
                            "the class attribute `{}.RUN` has to be from type list".format(cur_class.__name__))
                    # check that all elements that are mentioned here exists in the parent's RUN class variable or are
                    # defined in this class
                    for cur_run_method in cur_class.RUN:
                        if not inspect.ismethod(cur_run_method) or \
                                not cur_run_method.__name__.startswith('test_'):
                            raise TypeError(
                                "the given element {} for class attribute `{}.RUN` is no valid test method".format(
                                    cur_run_method.__name__, cur_class.__name__))
                        if cur_run_method not in cur_class.__dict__.values():
                            if next_parent is None:
                                raise ValueError(
                                    "the element `{}` given at class attribute `{}.RUN` is not a test method of this "
                                    "scenario".format(cur_run_method.__name__, cur_class.__name__))
                            else:
                                if cur_run_method in next_parent.IGNORE:
                                    raise ValueError(
                                        "the element `{}` given at class attribute `{}.RUN` was already added to "
                                        "IGNORE in a higher parent class - not possible to add it now to RUN".format(
                                            cur_run_method.__name__, cur_class.__name__))
                                elif cur_run_method in next_parent.SKIP:
                                    raise ValueError(
                                        "the element `{}` given at class attribute `{}.RUN` was already added to "
                                        "SKIP in a higher parent class - not possible to add it now to RUN".format(
                                            cur_run_method.__name__, cur_class.__name__))
                                elif cur_run_method not in next_parent.RUN:
                                    raise ValueError(
                                        "the element `{}` given at class attribute `{}.RUN` is not a test method of "
                                        "this scenario".format(cur_run_method.__name__, cur_class.__name__))
                else:
                    # RUN is not mentioned in this specific class -> so add an empty list for further access
                    cur_class.RUN = []

                # also add all in this class defined test methods to this RUN list
                for cur_item_name, cur_item in cur_class.__dict__.items():
                    if cur_item_name.startswith("test_") and inspect.ismethod(cur_item):
                        cur_class.RUN.append(cur_item)
                # now add all items from parent classes to the lists that are not mentioned yet
                if next_parent is not None:
                    for cur_parent_run_method in next_parent.RUN:
                        if cur_parent_run_method not in cur_class.RUN and cur_parent_run_method not in cur_class.SKIP \
                                and cur_parent_run_method not in cur_class.IGNORE:
                            cur_class.RUN.append(cur_parent_run_method)
                    for cur_parent_skip_method in next_parent.SKIP:
                        if cur_parent_skip_method not in cur_class.SKIP \
                                and cur_parent_skip_method not in cur_class.IGNORE:
                            cur_class.SKIP.append(cur_parent_skip_method)
                    for cur_parent_ignore_method in next_parent.IGNORE:
                        if cur_parent_ignore_method not in cur_class.IGNORE:
                            cur_class.IGNORE.append(cur_parent_ignore_method)

    @staticmethod
    def rework_method_variation_decorators():
        """
        This method iterates over the static attribute `Collector._possible_method_variations` and checks if these
        decorated functions are valid (if they are methods of a :meth:`Feature` class). All valid decorated data will
        then be set for the related feature classes.
        """

        for cur_fn, cur_decorator_data_list in Collector._possible_method_variations.items():
            owner = get_class_that_defines_method(cur_fn)
            owner_feature_controller = FeatureController.get_for(owner)
            name = cur_fn.__name__

            owner_for_vdevice = owner_feature_controller.get_method_based_for_vdevice()
            if owner_for_vdevice is None:
                owner_for_vdevice = {}
            for cur_decorator_vdevice, cur_decorator_with_connections in cur_decorator_data_list:

                if owner is None:
                    raise TypeError("The use of the `@for_vdevice` decorator is only allowed for `Feature` objects and "
                                    "methods of `Feature` objects")
                if not issubclass(owner, Feature):
                    raise TypeError(f"The use of the `for_vdevice` decorator is not allowed for methods of a "
                                    f"`{owner.__name__}`. You should only use this decorator for `Feature` elements")

                if isinstance(cur_decorator_vdevice, str):
                    # vDevice is a string, so we have to convert it to the correct class
                    relevant_vdevices = [cur_vdevice for cur_vdevice
                                         in owner_feature_controller.get_abs_inner_vdevice_classes()
                                         if cur_vdevice.__name__ == cur_decorator_vdevice]
                    if len(relevant_vdevices) == 0:
                        raise ValueError(f"can not find a matching inner VDevice class for the given vdevice string "
                                         f"`{cur_decorator_vdevice}` in the feature class `{owner.__name__}`")
                    elif len(relevant_vdevices) > 1:
                        raise RuntimeError("found more than one possible vDevices - something unexpected happened")
                    cur_decorator_vdevice = relevant_vdevices[0]

                if cur_decorator_vdevice not in owner_feature_controller.get_abs_inner_vdevice_classes():
                    raise UnknownVDeviceException(f"the given vDevice `{cur_decorator_vdevice.__name__}` is not a "
                                                  f"usable vDevice in Feature class `{owner.__name__}`")

                if name not in owner_for_vdevice.keys():
                    owner_for_vdevice[name] = {}

                cur_decorator_cleaned_cnns = []
                for cur_cnn in cur_decorator_with_connections:
                    if isinstance(cur_cnn, type) and issubclass(cur_cnn, Connection):
                        cur_cnn = cur_cnn()
                    cur_decorator_cleaned_cnns.append(cur_cnn)

                if cur_fn in owner_for_vdevice[name].keys():
                    old_dict = owner_for_vdevice[name][cur_fn]
                    if cur_decorator_vdevice in old_dict.keys():
                        raise DuplicateForVDeviceError(f'there already exists a decorator for the vDevice '
                                                       f'`{cur_decorator_vdevice}` at method `{name}` of class '
                                                       f'`{owner.__name__}` ')

                    old_dict[cur_decorator_vdevice] = cur_decorator_cleaned_cnns
                    owner_for_vdevice[name][cur_fn] = old_dict
                else:
                    new_dict = {cur_decorator_vdevice: cur_decorator_cleaned_cnns}
                    owner_for_vdevice[name][cur_fn] = new_dict

            def owner_wrapper(the_owner_of_this_method, the_name):
                @functools.wraps(cur_fn)
                def method_variation_multiplexer(this, *args, **kwargs):
                    if this.__class__ == the_owner_of_this_method:
                        # this is no parent class call -> use the set method-variation (set by VariationExecutor before)
                        _, _, func = this._active_method_variations.get(the_name, None)
                    else:
                        func = this._get_inherited_method_variation(the_owner_of_this_method, the_name)
                        if func is None:
                            raise AttributeError(f'there exists no method/method variation in class '
                                                 f'`{the_owner_of_this_method.__name__}` or its parent classes')
                    if len(args) == 0:
                        return func(self=this, **kwargs)
                    else:
                        new_args = [this, *args]
                        return func(*new_args)
                return method_variation_multiplexer

            new_callback = owner_wrapper(owner, name)
            setattr(owner, name, new_callback)
            owner_feature_controller.set_method_based_for_vdevice(owner_for_vdevice)

    def exchange_device_connection_device_strings(self):
        """
        This method ensures that device names that are provided as strings within connections are resolved for each
        connection object of a device. Since the `@connect` marker makes it possible to specify the other device as a
        string, this method matches all connection objects of this device to convert the strings into the correct
        device types.

        In some cases you have to provide the devices for the decorator as a string (since the outer class is imported
        later than the execution of the decorator). Balder knows this information after the decorator has been executed,
        so it is required to convert these strings now.
        """
        all_devices = []
        for cur_setup in self._all_setups:
            for cur_device in SetupController.get_for(cur_setup).get_all_inner_device_classes():
                all_devices.append(cur_device)
        for cur_scenario in self._all_scenarios:
            for cur_device in ScenarioController.get_for(cur_scenario).get_all_inner_device_classes():
                all_devices.append(cur_device)

        for cur_device in all_devices:
            cur_device_controller = DeviceController.get_for(cur_device)
            for cur_node in cur_device_controller.connections.keys():
                for cur_conn in cur_device_controller.connections[cur_node]:
                    # for every connection applies that the `from_device` must already be a type; also the
                    # `to_device` has to be an inner class of this type

                    if isinstance(cur_conn.to_device, type) and issubclass(cur_conn.to_device, Device):
                        # Skip because resolving already done
                        return

                    # get outer class of `from_device`
                    outer_cls_name_from_device = cur_conn.from_device.__qualname__.rpartition('.')[0]
                    mod = sys.modules[cur_conn.from_device.__module__]
                    parent_cls_from_device = getattr(mod, outer_cls_name_from_device)

                    all_outer_inner_classes = inspect.getmembers(parent_cls_from_device, inspect.isclass)
                    all_outer_inner_classes = {name: value for name, value in all_outer_inner_classes}
                    if cur_conn.to_device in all_outer_inner_classes.keys():
                        meta = cur_conn.metadata

                        meta["to_device"] = all_outer_inner_classes[cur_conn.to_device]
                        if meta["to_device_node_name"] is None:
                            # no unique node was given -> create one
                            meta["to_device_node_name"] = \
                                DeviceController.get_for(meta["to_device"]).get_new_empty_auto_node()

                        # first reset whole metadata
                        cur_conn.metadata = {}
                        # now set metadata
                        cur_conn.metadata = meta
                    else:
                        raise DeviceResolvingException(
                            f"cannot resolve the str for the given device class `{cur_conn.to_device}` for "
                            f"`@connect` decorator at device `{cur_conn.from_device.__qualname__}`")

    def exchange_vdevice_mapping_device_strings(self):
        """
        This method iterates over every collected :class:`.Setup` and :class:`.Scenario` device and updates the inner
        VDevice-Device mappings for every instantiated :class:`.Feature`, if the mapped device (value in constructor)
        is given as a string.
        """
        def exchange_string_for_vdevice_class_in(device: Type[Device], in_classes: List[Type[Device]]):
            all_instanced_features = DeviceController.get_for(device).get_original_instanced_feature_objects()
            if all_instanced_features is None:
                # has no features -> skip
                return
            for _, cur_feature in all_instanced_features.items():
                if cur_feature.active_vdevices != {}:
                    # do something only if there exists an internal mapping
                    for cur_mapped_vdevice, cur_mapped_device in cur_feature.active_vdevices.items():
                        if isinstance(cur_mapped_device, str):
                            resolved_device = [cur_possible_device for cur_possible_device in in_classes
                                               if cur_possible_device.__name__ == cur_mapped_device]
                            if len(resolved_device) != 1:
                                raise RuntimeError(
                                    f"found none or more than one possible name matching while trying to resolve "
                                    f"the given vDevice string `{cur_mapped_vdevice}` in feature "
                                    f"`{cur_feature.__class__.__name__}`")
                            cur_feature.active_vdevices[cur_mapped_vdevice] = resolved_device[0]

        for cur_scenario in self._all_scenarios:
            scenario_devices = ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes()
            for cur_device in scenario_devices:
                exchange_string_for_vdevice_class_in(device=cur_device, in_classes=scenario_devices)
        for cur_setup in self._all_setups:
            setup_devices = SetupController.get_for(cur_setup).get_all_abs_inner_device_classes()
            for cur_device in setup_devices:
                exchange_string_for_vdevice_class_in(device=cur_device, in_classes=setup_devices)

    def get_all_scenario_feature_classes(self) -> List[Type[Feature]]:
        """
        This method returns a list with all :class:`Feature` classes that are being instantiated in one or more
        :class:`Scenario` classes.

        :return: a list with all :class:`Feature` classes
        """
        all_scenario_features = []
        for cur_scenario in self._all_scenarios:
            for cur_device in ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes():
                all_instantiated_features = DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
                for _, cur_feature_obj in all_instantiated_features.items():
                    if cur_feature_obj.__class__ not in all_scenario_features:
                        all_scenario_features.append(cur_feature_obj.__class__)
        return all_scenario_features

    def get_all_setup_feature_classes(self) -> List[Type[Feature]]:
        """
        This method returns a list with all :class:`Feature` classes that are instantiated in :class:`Setup` class
        devices.

        :return: a list with all :class:`Feature` classes
        """
        all_setup_features = []
        for cur_setup in self._all_setups:
            for cur_device in SetupController.get_for(cur_setup).get_all_abs_inner_device_classes():
                cur_device_instantiated_features = \
                    DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
                for _, cur_feature_obj in cur_device_instantiated_features.items():
                    if cur_feature_obj.__class__ not in all_setup_features:
                        all_setup_features.append(cur_feature_obj.__class__)
        return all_setup_features

    def get_all_scenario_device_classes(self) -> List[Type[Device]]:
        """
        This method returns a list with all inner :class:`Device` classes that are defined in one of the collected
        :class:`.Scenario` classes.

        :return: a list with all :class:`Device` classes
        """
        all_scenario_devices = []
        for cur_scenarios in self._all_scenarios:
            all_scenario_devices += ScenarioController.get_for(cur_scenarios).get_all_abs_inner_device_classes()
        return all_scenario_devices

    def get_all_setup_device_classes(self) -> List[Type[Device]]:
        """
        This method returns a list with all inner :class:`Device` classes that are defined in one of the collected
        :class:`.Setup` classes.

        :return: a list with all :class:`Device` classes
        """
        all_setup_devices = []
        for cur_setup in self._all_setups:
            all_setup_devices += SetupController.get_for(cur_setup).get_all_abs_inner_device_classes()
        return all_setup_devices

    @staticmethod
    def validate_feature_inheritance_of(devices: List[Type[Device]]):
        """
        This method validates instantiated features and check that they are inherited correctly. It checks that the
        feature of a child device is also a child class of the feature of the parent device (in case they use the same
        property name).
        """

        for cur_device in devices:
            all_instantiated_feature_objs = DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
            # only one match possible, because we already have checked it before
            next_base_device = [base_device for base_device in cur_device.__bases__ if issubclass(base_device, Device)]
            if next_base_device[0] != Device:
                # also execute this method for the base device
                Collector.validate_feature_inheritance_of(next_base_device)
                all_parent_instantiated_feature_objs = \
                    DeviceController.get_for(next_base_device[0]).get_all_instantiated_feature_objects()
            else:
                all_parent_instantiated_feature_objs = {}

            for cur_attr_name, cur_feature in all_instantiated_feature_objs.items():
                if cur_attr_name in all_parent_instantiated_feature_objs.keys():
                    # attribute name also exists before -> check if the feature is a parent of the current one
                    if not isinstance(cur_feature, all_parent_instantiated_feature_objs[cur_attr_name].__class__):
                        raise FeatureOverwritingError(
                            f"the feature `{cur_feature.__class__.__name__}` with the attribute name `{cur_attr_name}` "
                            f"of the device `{cur_device.__name__}` you are trying to overwrite is no child class of "
                            f"the feature `{all_parent_instantiated_feature_objs[cur_attr_name].__class__.__name__}` "
                            f"that was assigned to this property before")

    @staticmethod
    def validate_inner_referenced_features(devices: List[Type[Device]]):
        """
        This method validates that every :class:`Feature` that is referenced from another :class:`Feature` also exists
        in the definition list of the current :class:`Scenario`-Device.
        """
        for cur_outer_device in devices:
            all_instantiated_feature_objs = \
                DeviceController.get_for(cur_outer_device).get_all_instantiated_feature_objects()
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
                                    "can not reference the same feature from itself (done in feature `{}` with "
                                    "`{}`)".format(cur_feature.__class__.__name__, cur_ref_feature_name))
                            potential_candidates.append(cur_potential_candidate_feature)
                    if len(potential_candidates) == 0:
                        raise InnerFeatureResolvingError(
                            "can not find a matching feature in the device `{}` that could be assigned to the "
                            "inner feature reference `{}` of the feature `{}`".format(
                                cur_outer_device.__name__, cur_ref_feature_name, cur_feature.__class__.__name__))
                    elif len(potential_candidates) > 1:
                        raise InnerFeatureResolvingError(
                            "found more than one matching feature in the device `{}` that could be assigned to "
                            "the inner feature reference `{}` of the feature `{}`".format(
                                cur_outer_device.__name__, cur_ref_feature_name, cur_feature.__class__.__name__))

    @staticmethod
    def set_original_device_features_for_all_vdevices_of(features: List[Type[Feature]]):
        """
        This method sets the important property `VDevice.__original_instanced_features` to ensure that the
        :class:`.VDevice` retains an original representation of its abstract features. The real features are
        overwritten for each new variation by the :class:`ExecutorTree`!

        :param features: all features the vDevices-Features should be saved for
        """
        for cur_feature in features:
            cur_feature_controller = FeatureController.get_for(cur_feature)
            vdevices = cur_feature_controller.get_abs_inner_vdevice_classes()
            for cur_vdevice in vdevices:
                cur_vdevice_controller = VDeviceController.get_for(cur_vdevice)
                new_originals = cur_vdevice_controller.get_all_instantiated_feature_objects()

                if cur_vdevice_controller.get_original_instanced_feature_objects():
                    if cur_vdevice_controller.get_original_instanced_feature_objects() != new_originals:
                        raise EnvironmentError(
                            f"the vDevice `{cur_vdevice.__name__}` already has a static attribute value in "
                            f"`Device.__original_instanced_features`")

                cur_vdevice_controller.set_original_instanced_feature_objects(new_originals)

    @staticmethod
    def feature_validate_inner_classes(features: List[Type[Feature]]):
        """
        This method validates all inner classes and secures that these classes are subclasses from :class:`VDevice` or
        no subclasses from :class:`Device` only! Of course other inner-classes that are not required for balder are
        allowed too.

        :param features: a list of all feature classes that should be validated here
        """
        for cur_feature in features:
            all_inner_classes = inspect.getmembers(cur_feature, inspect.isclass)
            for cur_inner_name, cur_inner_class in all_inner_classes:
                if issubclass(cur_inner_class, Device):
                    # do only check the inner classes that inherits from `Device`
                    if not issubclass(cur_inner_class, VDevice):
                        raise VDeviceResolvingError(
                            f"the inner class `{cur_inner_class.__name__}` with name `{cur_inner_name}` is a child "
                            f"class of `Device` but not from `VDevice` as expected")
                    cur_inner_class_instantiated_features = \
                        VDeviceController.get_for(cur_inner_class).get_all_instantiated_feature_objects()
                    for _, cur_vdevice_feature in cur_inner_class_instantiated_features.items():
                        if cur_vdevice_feature.active_vdevices != {}:
                            raise IllegalVDeviceMappingError(
                                f"the feature `{cur_vdevice_feature.__class__.__name__}` you have instantiated in your "
                                f"vDevice `{cur_inner_class.__name__}` of feature `{cur_feature.__name__}` "
                                f"has a own vDevice mapping - vDevice mappings are allowed for features on Devices "
                                f"only")

    @staticmethod
    def feature_validate_vdevice_inheritance(features: List[Type[Feature]]):
        """
        This method validates all inner :class:`VDevice` classes and secures that the inheritance of them is correct.

        It secures that new :class:`VDevice` classes are added or existing :class:`VDevice` classes are completely being
        overwritten for one feature level. The method only allows the overwriting of :class:`VDevices`, which are child
        classes of another :class:`VDevice` that is defined in a parent :class:`Feature` class. In addition, the
        class has to have the same name as its parent class.

        The method also secures that the user overwrites instantiated :class:`Feature` classes in the VDevice (class
        property name is the same) only with subclasses of the element that is being overwritten. New Features can be
        added without consequences.

        :param features: those are all feature classes that are being checked if their inner vDevices classes were
                         inherited
        """

        # validate that all parent VDevices are overwritten if one or more VDevice(s) are defined in current feature
        for cur_feature in features:
            all_direct_vdevices_of_this_feature_lvl = \
                FeatureController.get_for(cur_feature).get_inner_vdevice_classes()
            if len(all_direct_vdevices_of_this_feature_lvl) != 0:
                # check that all absolute items of higher class are implemented
                next_feature_parent = None
                for cur_parent in cur_feature.__bases__:
                    if issubclass(cur_parent, Feature) and cur_parent != Feature:
                        if next_feature_parent is not None:
                            raise MultiInheritanceError(
                                "can not select the next parent class, found more than one parent classes for feature "
                                f"`{cur_feature.__class__.__name__}` that is a subclass of `{Feature.__name__}`")
                        next_feature_parent = cur_parent
                # only continue if the current feature has a parent class
                if next_feature_parent:
                    # first check the parent feature (maybe the error has already occurred before)
                    Collector.feature_validate_vdevice_inheritance([next_feature_parent])

                    parent_vdevices = FeatureController.get_for(next_feature_parent).get_abs_inner_vdevice_classes()
                    # now check for every parent vDevice if it also exists in the current selection
                    for cur_parent_vdevice in parent_vdevices:
                        direct_namings = [cur_item.__name__ for cur_item in all_direct_vdevices_of_this_feature_lvl]
                        # check that the parent vDevice exists in the direct namings
                        if cur_parent_vdevice.__name__ not in direct_namings:
                            raise VDeviceOverwritingError(
                                f"missing overwriting of parent VDevice class `{cur_parent_vdevice.__qualname__}` in "
                                f"feature class `{cur_feature.__name__}` - if you overwrite one or more VDevice(s) "
                                f"you have to overwrite all!")
                        else:
                            # otherwise check if inheritance AND feature overwriting is correct
                            cur_child_idx = direct_namings.index(cur_parent_vdevice.__name__)
                            related_child_vdevice = all_direct_vdevices_of_this_feature_lvl[cur_child_idx]
                            if not issubclass(related_child_vdevice, cur_parent_vdevice):
                                # inherit from a parent device, but it has not the same naming -> NOT ALLOWED
                                raise VDeviceOverwritingError(
                                        f"the inner vDevice class `{related_child_vdevice.__qualname__}` has the same "
                                        f"name than the vDevice `{cur_parent_vdevice.__qualname__}` - it should also "
                                        f"inherit from it")
                            # todo check that feature overwriting inside the VDevice is correct
                            # now check that the vDevice overwrites the existing properties only in a proper manner (to
                            #  overwrite it, it has to have the same property name as the property in the next parent
                            #  class)
                            cur_vdevice_features = \
                                VDeviceController.get_for(related_child_vdevice).get_all_instantiated_feature_objects()
                            cur_vdevice_base_features = \
                                VDeviceController.get_for(cur_parent_vdevice).get_all_instantiated_feature_objects()
                            for cur_base_property_name, cur_base_feature_instance in cur_vdevice_base_features.items():
                                # now check that every base property is available in the current vDevice too - check
                                #  that the instantiated feature is the same or the feature of the child vDevice is a
                                #  child of it -> ignore it, if the child vDevice has more features than the base -
                                #   that doesn't matter
                                if cur_base_property_name not in cur_vdevice_features.keys():
                                    raise VDeviceResolvingError(
                                        f"can not find the property `{cur_base_property_name}` of "
                                        f"parent vDevice `{cur_parent_vdevice.__qualname__}` in the "
                                        f"current vDevice class `{related_child_vdevice.__qualname__}`")
                                cur_feature_instance = cur_vdevice_features[cur_base_property_name]
                                if not isinstance(cur_feature_instance, cur_base_feature_instance.__class__):
                                    raise FeatureOverwritingError(
                                        f"you are trying to overwrite an existing vDevice Feature property "
                                        f"`{cur_base_property_name}` in vDevice `{related_child_vdevice.__qualname__}` "
                                        f"from the parent vDevice class `{cur_parent_vdevice.__qualname__}` - this is "
                                        f"only possible with a child (or with the same) feature class the parent "
                                        f"uses (in this case the `{cur_base_feature_instance.__class__.__name__}`)")

    @staticmethod
    def feature_determine_class_for_vdevice_values(features: List[Type[Feature]], print_warning=True):
        """
        This method determines the absolute class based values for `@for_vdevice`. It will do nothing if the value was
        already set by an explicit class based `@for_vdevice` decorator. In this case the method only checks that
        every given vDevice class is a real part of the current :class:`Feature` class (will be returned by direct call
        of method `Feature.get_inner_vdevice_classes()`). Otherwise, it determines the class based `@for_vdevice`
        value through analysing of the method based decorators and sets this determined value. If the method has to
        determine the value, it throws a warning with a suggestion for a nice class based decorator. Also, here the
        method will analyse the given vDevice classes and secures that they are defined in the current :class:`Feature`
        class.

        .. note::
            This method automatically updates the values for the parent classes, too. Every time it searches for the
            values it considers the parent values for the vDevice or the parent class of the vDevice, too.

        .. note::
            This method can throw a user warning (`throw_warning` has to be True for that), but only on the given list
            of :class:`Feature` classes. All parent :class:`Feature` classes will be determined correctly, but will not
            throw a waring.
        """
        for cur_feature in features:
            cur_feature_controller = FeatureController.get_for(cur_feature)
            # first determine this for all parent classes
            to_determining_features = [
                cur_cls for cur_cls in cur_feature.__bases__ if issubclass(cur_cls, Feature) and cur_cls != Feature]
            # with the following recursive call we guarantee that every parent class has the correct resolved class
            #  based @for_vdevice information
            Collector.feature_determine_class_for_vdevice_values(to_determining_features, False)
            # now check if a definition for this class exists
            all_vdevices = cur_feature_controller.get_abs_inner_vdevice_classes()
            # check the class based @for_vdevice and check the used vDevice classes here
            if cur_feature_controller.get_class_based_for_vdevice() is not None:
                for cur_decorated_vdevice in cur_feature_controller.get_class_based_for_vdevice().keys():
                    if cur_decorated_vdevice not in all_vdevices:
                        raise VDeviceResolvingError(
                            f"you assign a vDevice to the class based decorator `@for_vdevice()` of the feature class "
                            f"`{cur_feature.__name__}` which is no direct member of this feature - note that you have "
                            f"to define the vDevice in your feature before using it in the decorator - if necessary "
                            f"overwrite it")
            # check the method based @for_vdevice and check the used vDevice classes here
            if cur_feature_controller.get_method_based_for_vdevice() is not None:
                for cur_method_name, cur_method_data in cur_feature_controller.get_method_based_for_vdevice().items():
                    for _, vdevice_dict in cur_method_data.items():
                        for cur_vdevice in vdevice_dict.keys():
                            if cur_vdevice not in all_vdevices:
                                raise VDeviceResolvingError(
                                    f"you assign a vDevice to the method variation `{cur_method_name}` of the feature "
                                    f"class `{cur_feature.__name__}` which is no direct member of this feature - note "
                                    f"that you have to use the overwritten version if you overwrite a vDevice")
            cur_feature_cls_for_vdevice = cur_feature_controller.get_class_based_for_vdevice()
            cur_feature_cls_for_vdevice = {} if cur_feature_cls_for_vdevice is None else cur_feature_cls_for_vdevice
            for cur_vdevice in all_vdevices:
                # determine the class based for_vdevice value only if there is no one defined for this vDevice
                if cur_vdevice not in cur_feature_cls_for_vdevice.keys() or \
                        len(cur_feature_cls_for_vdevice[cur_vdevice]) == 0:
                    # first determine the valid parent intersection (can also be extended itself)

                    # get the correct vDevice that is known in the parent feature class
                    if VDeviceController.get_for(cur_vdevice).get_outer_class() == cur_feature:
                        # this cur_vdevice is (newly) defined in this Feature class -> can't exist in one of the parent
                        #  classes
                        #  -> search parent vDevice existence (if there is a parent vDevice, this vDevice is also in our
                        #     parent feature class)
                        #  -> if it does not exist -> there is no parent class based definition
                        possible_vdevices_of_interest = []
                        for cur_vdevice_of_interest in cur_vdevice.__bases__:
                            if issubclass(cur_vdevice_of_interest, VDevice) and cur_vdevice_of_interest != VDevice:
                                possible_vdevices_of_interest.append(cur_vdevice_of_interest)
                        if len(possible_vdevices_of_interest) > 1:
                            raise VDeviceResolvingError(
                                f"the vdevice `{cur_vdevice.__name__}` has more than one parent classes from type "
                                f"`VDevice` - this is not allowed")
                        elif len(possible_vdevices_of_interest) == 1:
                            # we have found one parent vDevice that has the same name as the cur_vdevice
                            vdevice_of_interest = possible_vdevices_of_interest[0]
                        else:
                            # we have no parent vDevice -> there are no parent ConnectionTree
                            vdevice_of_interest = None

                    else:
                        # the definition scope of the VDevice is in a higher Feature parent -> has to be in the
                        # `__cls_for_vdevice` in one of the next base classes
                        vdevice_of_interest = cur_vdevice

                    parent_values = []
                    # read vDevice connection tree of parent feature class (only if the vDevice already exists in the
                    # parent class)
                    if vdevice_of_interest is not None:
                        for cur_feature_base in to_determining_features:
                            cur_feature_base_cls_for_vdevice = \
                                FeatureController.get_for(cur_feature_base).get_class_based_for_vdevice()
                            cur_feature_base_cls_for_vdevice = {} if cur_feature_base_cls_for_vdevice is None else \
                                cur_feature_base_cls_for_vdevice
                            if vdevice_of_interest in cur_feature_base_cls_for_vdevice.keys():
                                for cur_cnn in cur_feature_base_cls_for_vdevice[vdevice_of_interest]:
                                    # clean metadata here because this is no connection between real devices
                                    cur_cnn.set_metadata_for_all_subitems(None)
                                    parent_values.append(cur_cnn)

                    this_vdevice_intersection = parent_values + []

                    # determine the class value automatically by discovering all method variations for this vDevice only
                    if cur_feature_controller.get_method_based_for_vdevice() is not None:
                        for _, method_dict in cur_feature_controller.get_method_based_for_vdevice().items():
                            for _, vdevice_dict in method_dict.items():
                                if cur_vdevice in vdevice_dict.keys():
                                    for cur_cnn in vdevice_dict[cur_vdevice]:
                                        if isinstance(cur_cnn, type):
                                            cur_cnn = cur_cnn()
                                        # clean metadata here because this is no connection between real devices
                                        cur_cnn.set_metadata_for_all_subitems(None)
                                        this_vdevice_intersection.append(cur_cnn)
                    else:
                        # there exists no method-variations
                        if cur_feature_controller.get_class_based_for_vdevice() is None:
                            # there exists also no class based decorator -> set the gobal tree
                            this_vdevice_intersection.append(Connection())
                    # set the determined data into the class based `@for_vdevice` class property
                    cur_feature_cls_for_vdevice[cur_vdevice] = this_vdevice_intersection
                    cur_feature_controller.set_class_based_for_vdevice(cur_feature_cls_for_vdevice)

                    # print warning only if the printing is enabled and there is a sub connection tree (otherwise, the
                    #  decorator is not necessary)
                    if print_warning and len(this_vdevice_intersection) > 0:
                        # only print the warning if there exists method variations for the feature
                        if cur_feature_controller.get_method_based_for_vdevice() is not None:
                            logger.warning(
                                f"your used feature class `{cur_feature.__name__}` doesn't provide a class based "
                                f"@for_vdevice decorator for the vDevice `{cur_vdevice.__name__}`\n"
                                f"Balder has determined a possible marker:\n\n"
                                f'@balder.for_vdevice("{cur_vdevice.__name__}", '
                                f'{", ".join([cur_cnn.get_tree_str() for cur_cnn in this_vdevice_intersection])})\n\n')

    @staticmethod
    def check_vdevice_feature_existence(items: Union[List[Type[Scenario]], List[Type[Setup]]]):
        """
        This method validates that all mapped VDevice connections exist in the related device. For this the method only
        checks the absolute VDevices on Setup/on Scenario level. Variations are not related to this and will not be
        checked here.
        """
        for cur_scenario_or_setup in items:
            cur_scenario_or_setup_controller = None
            if issubclass(cur_scenario_or_setup, Scenario):
                cur_scenario_or_setup_controller = ScenarioController.get_for(cur_scenario_or_setup)
            elif issubclass(cur_scenario_or_setup, Setup):
                cur_scenario_or_setup_controller = SetupController.get_for(cur_scenario_or_setup)

            for cur_device in cur_scenario_or_setup_controller.get_all_abs_inner_device_classes():
                cur_device_instantiated_features = \
                    DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
                for cur_attr_name, cur_feature in cur_device_instantiated_features.items():
                    active_vdevice, related_device = cur_feature.active_vdevice_device_mapping
                    if active_vdevice is not None:
                        # check that all the defined features in the VDevice also exist in the related device ->
                        #  otherwise error
                        orig_features = [
                            feat for _, feat in
                            DeviceController.get_for(related_device).get_all_instantiated_feature_objects().items()]
                        active_vdevice_instantiated_features = \
                            VDeviceController.get_for(active_vdevice).get_all_instantiated_feature_objects()
                        for _, cur_vdevice_feature in active_vdevice_instantiated_features.items():
                            # search for it
                            found_it = False
                            for cur_orig_feature in orig_features:
                                if isinstance(cur_orig_feature, cur_vdevice_feature.__class__):
                                    found_it = True
                                    break
                            if not found_it:
                                raise Exception(
                                    f"the device `{related_device.__name__}` which is mapped to the VDevice "
                                    f"`{active_vdevice.__name__}` doesn't have an implementation for the feature "
                                    f"`{cur_vdevice_feature.__class__.__name__}` required by the VDevice class "
                                    f"`{active_vdevice.__name__}`")

    @staticmethod
    def feature_check_inherited_vdevice_class_connection_subset(features: List[Type[Feature]]):
        """
        This method checks that the class based for_vdevice values of a child :class:`Feature` class are contained_in
        the related VDevice defined in a parent :class:`Feature` class.
        """

        to_checking_features = []
        for cur_feature in features:
            cur_feature_controller = FeatureController.get_for(cur_feature)
            feature_vdevices = cur_feature_controller.get_abs_inner_vdevice_classes()
            for cur_vdevice in feature_vdevices:
                cur_vdevice_cls_cnn = cur_feature_controller.get_class_based_for_vdevice().get(cur_vdevice)
                # get parent class of vdevice
                relevant_parent_class = None
                for cur_vdevice_base_cls in cur_vdevice.__bases__:
                    if issubclass(cur_vdevice_base_cls, VDevice) and cur_vdevice_base_cls != VDevice:
                        relevant_parent_class = cur_vdevice_base_cls
                        relevant_parent_class_controller = VDeviceController.get_for(relevant_parent_class)
                        while relevant_parent_class != VDevice and \
                                relevant_parent_class_controller.get_outer_class() == cur_feature:
                            for cur_vdevice_base_of_base_cls in relevant_parent_class.__bases__:
                                if issubclass(cur_vdevice_base_of_base_cls, VDevice):
                                    relevant_parent_class = cur_vdevice_base_of_base_cls
                                    if relevant_parent_class == VDevice:
                                        break
                                    if relevant_parent_class_controller.get_outer_class() != cur_feature:
                                        # found next vDevice in another Feature
                                        break
                        if relevant_parent_class != VDevice:
                            break
                if relevant_parent_class is not None and relevant_parent_class != VDevice:
                    relevant_parent_class_controller = VDeviceController.get_for(relevant_parent_class)
                    # only if there is a higher class which has to be considered
                    parent_vdevice_feature = relevant_parent_class_controller.get_outer_class()
                    if parent_vdevice_feature not in to_checking_features:
                        to_checking_features.append(parent_vdevice_feature)
                    parent_vdevice_cnn = \
                        FeatureController.get_for(
                            parent_vdevice_feature).get_class_based_for_vdevice()[relevant_parent_class]
                    # check if VDevice connection elements are all contained in the parent connection
                    for cur_element in cur_vdevice_cls_cnn:
                        if isinstance(cur_element, tuple):
                            if not Connection.check_if_tuple_contained_in_connection(
                                    cur_element, Connection.based_on(*parent_vdevice_cnn)):
                                raise VDeviceResolvingError(
                                    f"the VDevice `{cur_vdevice.__name__}` is a child of the VDevice "
                                    f"`{relevant_parent_class.__name__}`, which doesn't implements the connection of "
                                    f"the child - the connection tuple `("
                                    f"{', '.join([cur_tuple_item.get_tree_str() for cur_tuple_item in cur_element])})´"
                                    f" is not contained in the connection-tree of the parent VDevice")
                        else:
                            if not cur_element.contained_in(
                                    Connection.based_on(*parent_vdevice_cnn), ignore_metadata=True):
                                raise VDeviceResolvingError(
                                    f"the VDevice `{cur_vdevice.__name__}` is a child of the VDevice "
                                    f"`{relevant_parent_class.__name__}`, which doesn't implements the connection of "
                                    f"the child - the connection element `{cur_element.get_tree_str()})´ is not "
                                    f"contained in the connection-tree of the parent VDevice")

        # check all features where we have found parent VDevices as inner-classes to check next inheritance levels
        if len(to_checking_features) > 0:
            Collector.feature_check_inherited_vdevice_class_connection_subset(to_checking_features)

    def determine_raw_absolute_device_connections_for(self, items: Union[List[Type[Scenario]], List[Type[Setup]]]):
        """
        This method determines and creates the basic `_absolute_connections` for the given scenarios or setups. Note,
        that this method only creates the class attribute and adds the synchronized connections (same on both sides if
        they are bidirectional). It does not analyse or take :class:`Feature` classes into consideration.
        """

        all_related_next_base_classes = {}
        for cur_scenario_or_setup in items:
            # determine next relevant base class
            next_base_class = None
            for cur_base in cur_scenario_or_setup.__bases__:
                if issubclass(cur_base, Scenario) or issubclass(cur_base, Setup):
                    if next_base_class is not None:
                        raise MultiInheritanceError(
                            f"the class `{cur_scenario_or_setup.__name__}` has multiple parent classes from type "
                            f"`Scenario` or `Setup`")
                    next_base_class = cur_base
            all_related_next_base_classes[cur_scenario_or_setup] = next_base_class
            # executed this method for all parents too
            if next_base_class != Scenario and next_base_class != Setup:
                self.determine_raw_absolute_device_connections_for([next_base_class])

        all_relevant_cnns = []
        for cur_scenario_or_setup in items:
            cur_scenario_or_setup_controller = None
            if issubclass(cur_scenario_or_setup, Scenario):
                cur_scenario_or_setup_controller = ScenarioController.get_for(cur_scenario_or_setup)
            elif issubclass(cur_scenario_or_setup, Setup):
                cur_scenario_or_setup_controller = SetupController.get_for(cur_scenario_or_setup)

            all_devices = cur_scenario_or_setup_controller.get_all_inner_device_classes()
            all_devices_as_strings = [search_device.__name__ for search_device in all_devices]

            next_base_class = all_related_next_base_classes[cur_scenario_or_setup]

            # check if the devices of the current item has minimum one own connect() decorator
            has_connect_decorator = False
            for cur_device in all_devices:
                cur_device_controller = DeviceController.get_for(cur_device)
                if len(cur_device_controller.connections) > 0:
                    has_connect_decorator = True
            if len(all_devices) == 0 and len(cur_scenario_or_setup_controller.get_all_abs_inner_device_classes()) > 0:
                # only the parent class has defined scenarios -> use absolute data from next parent
                #  NOTHING TO DO, because we also use these devices in child setup/scenario
                return
            elif len(all_devices) > 0 and not has_connect_decorator:
                # the current item has defined devices, but no own `@connect()` decorator -> use absolute data from
                #  next parent

                if next_base_class != Scenario and next_base_class != Setup:
                    next_base_class_controller = None
                    if issubclass(next_base_class, Scenario):
                        next_base_class_controller = ScenarioController.get_for(next_base_class)
                    elif issubclass(next_base_class, Setup):
                        next_base_class_controller = SetupController.get_for(next_base_class)

                    for cur_parent_cnn in next_base_class_controller.get_all_abs_connections():

                        # find all related devices (for this connection)
                        related_from_device = \
                            all_devices[all_devices_as_strings.index(cur_parent_cnn.from_device.__name__)]
                        related_to_device = all_devices[all_devices_as_strings.index(cur_parent_cnn.to_device.__name__)]
                        new_cnn = cur_parent_cnn.clone()
                        new_cnn.set_metadata_for_all_subitems(None)
                        new_cnn.set_metadata_for_all_subitems(
                            {"from_device": related_from_device, "to_device": related_to_device,
                             "from_device_node_name": cur_parent_cnn.from_node_name,
                             "to_device_node_name": cur_parent_cnn.to_node_name})
                        all_relevant_cnns.append(new_cnn)

                    # throw warning (but only if this scenario/setup is a collected one, and minimum one of the parent
                    # classes has inner devices (and connection between them) by its own)
                    if len(next_base_class_controller.get_all_abs_inner_device_classes()) > 0 and \
                            len(next_base_class_controller.get_all_abs_connections()) > 0:
                        if cur_scenario_or_setup in self._all_scenarios or cur_scenario_or_setup in self._all_setups:
                            # this element is a collected one -> throw warning
                            logger.warning(
                                f"the collected `{cur_scenario_or_setup.__name__}` class overwrites devices, but does "
                                f"not define connections between them by its own - please provide them in case you "
                                f"overwrite devices")
            else:
                # otherwise, use data from current layer, because there is no parent, no devices or this item overwrites
                # the connections from higher classes
                for cur_device in all_devices:
                    cur_device_controller = DeviceController.get_for(cur_device)
                    for cur_node, cur_cnn_list in cur_device_controller.connections.items():
                        # now add every single connection correctly into the dictionary
                        for cur_cnn in cur_cnn_list:
                            if cur_cnn not in all_relevant_cnns:
                                all_relevant_cnns.append(cur_cnn)

            # now set the absolute connections correctly
            for cur_cnn in all_relevant_cnns:
                cur_cnn_from_device_controller = DeviceController.get_for(cur_cnn.from_device)
                cur_cnn_to_device_controller = DeviceController.get_for(cur_cnn.to_device)

                cur_cnn_from_device_controller.add_new_absolute_connection(cur_cnn)
                cur_cnn_to_device_controller.add_new_absolute_connection(cur_cnn)

    def validate_feature_clearance_for_parallel_connections_for_scenarios(self, scenarios: List[Type[Scenario]]):
        """
        This method validates for every active class-based feature (only the active one), that there exist a clear
        scenario-device-connection for this feature. The method throws a `UnclearAssignableFeatureConnectionError` if
        it can not determine a clear connection for a feature if there exists more than one possible device-connection
        for the related devices.
        """
        for cur_scenario in scenarios:
            all_devices = ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes()
            for cur_from_device in all_devices:
                # determine all VDevice-Device mappings for this one, by iterating over all instantiated Feature classes
                cur_from_device_instantiated_features = \
                    DeviceController.get_for(cur_from_device).get_all_instantiated_feature_objects()
                for _, cur_feature in cur_from_device_instantiated_features.items():
                    mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                    if mapped_device is None:
                        # ignore this, because we have no vDevices here
                        continue
                    else:
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
                        for cur_node, all_connections in mapped_device_abs_cnns.items():
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

    def determine_absolute_device_connections_for_scenarios(self, items: List[Type[Scenario]]):
        """
        This method determines the real possible Sub-Connections for every element of the scenarios. For this the method
        will create a possible intersection connection, for the :class:´Connection´ between two devices and
        all :class:`Connection`-Subtrees that are allowed for the mapped vDevices in the used :class:`Feature`
        classes.
        The data will be saved in the :class:`Device` property ``_absolute_connections``. If the method detects an empty
        intersection between two devices that are connected through a VDevice-Device mapping, the method will throw an
        exception.
        """
        reduction_candidates = {}

        def add_reduction_candidate(scenario, device, other_device):
            if scenario not in reduction_candidates.keys():
                reduction_candidates[scenario] = []
            if (device, other_device) not in reduction_candidates[scenario] and \
                    (other_device, device) not in reduction_candidates[scenario]:
                # we have to add it
                reduction_candidates[scenario].append((device, other_device))

        # start to generate the singles for every connection between the devices of every scenario
        all_abs_single_connections: \
            Dict[Type[Scenario], Dict[Type[Device], Dict[str, Dict[Type[Device], Dict[str, List[Connection]]]]]] = {}
        for cur_scenario in items:
            if cur_scenario not in all_abs_single_connections.keys():
                all_abs_single_connections[cur_scenario] = {}
            all_devices = ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes()
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
                        if cur_from_device not in all_abs_single_connections[cur_scenario].keys():
                            all_abs_single_connections[cur_scenario][cur_from_device] = {}
                        if cur_from_node not in all_abs_single_connections[cur_scenario][cur_from_device].keys():
                            all_abs_single_connections[cur_scenario][cur_from_device][cur_from_node] = {}
                        if cur_to_device not in \
                                all_abs_single_connections[cur_scenario][cur_from_device][cur_from_node].keys():
                            all_abs_single_connections[cur_scenario][cur_from_device][
                                cur_from_node][cur_to_device] = {}
                        if cur_to_node not in all_abs_single_connections[cur_scenario
                                ][cur_from_device][cur_from_node][cur_to_device].keys():
                            all_abs_single_connections[cur_scenario][cur_from_device][cur_from_node][cur_to_device][
                                cur_to_node] = cur_cnn.get_singles()
                            # we do not have to set the connection in communication device, because the absolute
                            # connections are always synchronized
                        else:
                            raise ValueError(
                                f'found multiple definitions for connection from device '
                                f'{cur_from_device.__qualname__} (node: `{cur_from_node}`) to device '
                                f'{cur_to_device.__qualname__} (node: `{cur_to_node}`) in scenario '
                                f'`{cur_scenario.__name__}`')

        for cur_scenario in items:
            all_devices = ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes()
            for cur_from_device in all_devices:
                # determine all VDevice-Device mappings for this one, by iterating over all instantiated Feature classes
                cur_from_device_instantiated_features = \
                    DeviceController.get_for(cur_from_device).get_all_instantiated_feature_objects()
                for _, cur_feature in cur_from_device_instantiated_features.items():
                    mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                    if mapped_device is None:
                        # ignore this, because we have no vDevices here
                        continue
                    else:
                        # now try to reduce the scenario connections according to the requirements of the feature class
                        cur_feature_class_based_for_vdevice = \
                            FeatureController.get_for(
                                cur_feature.__class__).get_class_based_for_vdevice()[mapped_vdevice]
                        feature_cnn = Connection.based_on(*cur_feature_class_based_for_vdevice)
                        # search node names that is the relevant connection
                        relevant_cnns: List[List[Connection]] = []
                        for _, cur_node_data in all_abs_single_connections[cur_scenario][cur_from_device].items():
                            for cur_to_device, cur_other_device_data in cur_node_data.items():
                                if cur_to_device == mapped_device:
                                    for _, cur_cnns in cur_other_device_data.items():
                                        relevant_cnns.append(cur_cnns)
                        device_cnn_singles = None
                        if len(relevant_cnns) > 1:
                            # there exists parallel connections - filter only the relevant one
                            for cur_single_cnns in relevant_cnns:
                                for cur_single_cnn in cur_single_cnns:
                                    if feature_cnn.contained_in(cur_single_cnn):
                                        # this is the relevant connection (all other can not fit, because we have
                                        # already checked this with method
                                        # `validate_feature_clearance_for_parallel_connections_for_scenarios`)
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
                            len(all_abs_single_connections[cur_scenario][cur_from_device][device_node_name][
                                    mapped_device][mapped_node_name])
                        for cur_abs_connection in \
                                all_abs_single_connections[cur_scenario][cur_from_device][device_node_name][
                                    mapped_device][mapped_node_name].copy():
                            if not feature_cnn.contained_in(cur_abs_connection, ignore_metadata=True):
                                # this abs single connection is not fulfilled by the current feature -> remove it
                                all_abs_single_connections[cur_scenario][cur_from_device][device_node_name][
                                    mapped_device][mapped_node_name].remove(cur_abs_connection)
                                add_reduction_candidate(cur_scenario, cur_from_device, mapped_device)
                        if start_length_before_reduction > 0 and \
                                len(all_abs_single_connections[cur_scenario][cur_from_device][device_node_name][
                                        mapped_device][mapped_node_name]) == 0:
                            raise ConnectionIntersectionError(
                                f"the `{cur_scenario.__name__}` has a connection from device "
                                f"`{cur_from_device.__name__}` to `{mapped_device.__name__}` - some mapped VDevices of "
                                f"their feature classes define mismatched connections")
                        # do the same for the opposite direction (features are always bidirectional)
                        start_length_before_reduction = \
                            len(all_abs_single_connections[cur_scenario][mapped_device][mapped_node_name][
                                    cur_from_device][device_node_name])
                        for cur_abs_connection in \
                                all_abs_single_connections[cur_scenario][mapped_device][mapped_node_name][
                                    cur_from_device][device_node_name].copy():
                            if not feature_cnn.contained_in(cur_abs_connection, ignore_metadata=True):
                                # this abs single connection is not being fulfilled by the current feature -> remove it
                                all_abs_single_connections[cur_scenario][mapped_device][mapped_node_name][
                                    cur_from_device][device_node_name].remove(cur_abs_connection)
                                add_reduction_candidate(cur_scenario, cur_from_device, mapped_device)
                        if start_length_before_reduction > 0 and \
                                len(all_abs_single_connections[cur_scenario][mapped_device][mapped_node_name][
                                        cur_from_device][device_node_name]) == 0:
                            raise ConnectionIntersectionError(
                                f"the `{cur_scenario.__name__}` has a connection from device "
                                f"`{cur_from_device.__name__}` to `{mapped_device.__name__}` - some mapped VDevices of "
                                f"their feature classes define mismatched connections")

        # generate all required warnings
        for cur_scenario, scenario_warning_list in reduction_candidates.items():
            for cur_warning_tuple in scenario_warning_list:
                logger.warning(f"detect some connections between the devices `{cur_warning_tuple[0].__name__}` and "
                               f"`{cur_warning_tuple[1].__name__}` of scenario `{cur_scenario.__name__}` that can be "
                               f"reduced, because their related features only use a subset of the defined connection")

        # first cleanup the relevant absolute connections
        for _, scenario_data in all_abs_single_connections.items():
            for cur_from_device, from_device_data in scenario_data.items():
                for _, from_node_date in from_device_data.items():
                    for cur_to_device, to_device_data in from_node_date.items():
                        cur_from_device_controller = DeviceController.get_for(cur_from_device)
                        cur_to_device_controller = DeviceController.get_for(cur_to_device)

                        cur_from_device_controller.cleanup_absolute_connections_with(cur_to_device)
                        cur_to_device_controller.cleanup_absolute_connections_with(cur_from_device)
        # replace all absolute connection with the single ones
        for cur_scenario, scenario_data in all_abs_single_connections.items():
            for cur_from_device, from_device_data in scenario_data.items():
                for cur_from_node, from_node_date in from_device_data.items():
                    for cur_to_device, to_device_data in from_node_date.items():
                        for cur_to_node, cur_single_cnns in to_device_data.items():

                            cur_from_device_controller = DeviceController.get_for(cur_from_device)
                            cur_to_device_controller = DeviceController.get_for(cur_to_device)

                            new_cnn = Connection.based_on(*cur_single_cnns)
                            new_cnn.set_metadata_for_all_subitems(cur_single_cnns[0].metadata)
                            if cur_from_device == cur_single_cnns[0].from_device:
                                cur_from_device_controller.add_new_absolute_connection(new_cnn)
                            else:
                                cur_to_device_controller.add_new_absolute_connection(new_cnn)

    @staticmethod
    def validate_feature_possibility_in_setups(setups: List[Type[Setup]]):
        """
        This method validates that every feature connection (that already has a vDevice<->Device mapping on setup level)
        has a connection that is CONTAINED-IN the connection of the related setup devices.
        """
        for cur_setup in setups:
            all_devices = SetupController.get_for(cur_setup).get_all_abs_inner_device_classes()
            for cur_device in all_devices:
                cur_device_instantiated_features = \
                    DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
                for _, cur_feature in cur_device_instantiated_features.items():
                    mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                    if mapped_device is None:
                        # ignore this, because we have no vDevice mapping on setup level
                        continue
                    else:
                        cur_feature_controller = FeatureController.get_for(cur_feature.__class__)
                        if cur_feature_controller.get_class_based_for_vdevice() and mapped_vdevice in \
                                cur_feature_controller.get_class_based_for_vdevice().keys():
                            # there exists a class based requirement for this vDevice
                            class_based_cnns = cur_feature_controller.get_class_based_for_vdevice()[mapped_vdevice]
                            class_based_cnn = Connection.based_on(*class_based_cnns)
                            # search relevant connection
                            cur_device_controller = DeviceController.get_for(cur_device)
                            for _, cur_cnn_list in cur_device_controller.get_all_absolute_connections().items():
                                for cur_cnn in cur_cnn_list:
                                    if cur_cnn.has_connection_from_to(cur_device, mapped_device):
                                        # check if the class-based feature connection is CONTAINED-IN this
                                        # absolute-connection
                                        if not class_based_cnn.contained_in(cur_cnn, ignore_metadata=True):

                                            raise IllegalVDeviceMappingError(
                                                f"the @for_vdevice connection for vDevice `{mapped_vdevice.__name__}` "
                                                f"of feature `{cur_feature.__class__.__name__}` (used in "
                                                f"`{cur_device.__qualname__}`) uses a connection that does not fit "
                                                f"with the connection defined in setup class "
                                                f"`{cur_device_controller.get_outer_class().__name__}` to related "
                                                f"device `{mapped_device.__name__}`")

    def collect(self, plugin_manager: PluginManager):
        """
        This method manages the entire collection process.

        :param plugin_manager: contains the reference to the used plugin manager
        """
        # load all py files
        self.load_balderglob_py_file()
        self._all_py_files = self.get_all_py_files()
        self._all_py_files = plugin_manager.execute_modify_collected_pyfiles(self._all_py_files)

        # collect all `Connection` classes (has to be first, because scenarios/setups can use them)
        self.load_all_connection_classes(py_file_paths=self._all_py_files)
        self._all_connections = self.get_all_connection_classes()

        # collect all `Scenario` classes
        self._all_scenarios = self.get_all_scenario_classes(
            py_file_paths=self._all_py_files, filter_abstracts=True)
        # collect all `Setup` classes
        self._all_setups = self.get_all_setup_classes(
            py_file_paths=self._all_py_files, filter_abstracts=True)

        self._all_scenarios, self._all_setups = plugin_manager.execute_collected_classes(
            scenarios=self._all_scenarios, setups=self._all_setups)

        self._all_scenarios = Collector.filter_parent_classes_of(items=self._all_scenarios)
        self._all_setups = Collector.filter_parent_classes_of(items=self._all_setups)

        all_scenario_features = self.get_all_scenario_feature_classes()
        all_setup_features = self.get_all_setup_feature_classes()

        Collector.rework_method_variation_decorators()

        Collector.validate_inheritance_of(self._all_scenarios)
        Collector.validate_inheritance_of(self._all_setups)

        # do some further stuff after everything was read
        self.set_original_device_features_for(self._all_scenarios)
        self.set_original_device_features_for(self._all_setups)
        Collector.resolve_raw_fixtures()
        Collector.set_original_device_features_for_all_vdevices_of(all_scenario_features)
        Collector.set_original_device_features_for_all_vdevices_of(all_setup_features)
        self.exchange_device_connection_device_strings()
        self.exchange_vdevice_mapping_device_strings()
        self.set_run_skip_ignore_of_test_methods_in_scenarios()

        Collector.validate_feature_inheritance_of(devices=self.get_all_scenario_device_classes())
        Collector.validate_feature_inheritance_of(devices=self.get_all_setup_device_classes())

        Collector.validate_inner_referenced_features(self.get_all_scenario_device_classes())
        Collector.validate_inner_referenced_features(self.get_all_setup_device_classes())

        Collector.feature_validate_inner_classes(all_scenario_features)
        Collector.feature_validate_inner_classes(all_setup_features)
        Collector.feature_validate_vdevice_inheritance(all_scenario_features)
        Collector.feature_validate_vdevice_inheritance(all_setup_features)
        Collector.feature_determine_class_for_vdevice_values(all_scenario_features)
        Collector.feature_determine_class_for_vdevice_values(all_setup_features)
        Collector.check_vdevice_feature_existence(self.all_scenarios)
        Collector.check_vdevice_feature_existence(self.all_setups)
        Collector.feature_check_inherited_vdevice_class_connection_subset(all_scenario_features)
        self.validate_feature_clearance_for_parallel_connections_for_scenarios(self.all_scenarios)
        self.determine_raw_absolute_device_connections_for(self.all_scenarios)
        self.determine_raw_absolute_device_connections_for(self.all_setups)
        self.determine_absolute_device_connections_for_scenarios(self.all_scenarios)
        Collector.validate_feature_possibility_in_setups(self.all_setups)
