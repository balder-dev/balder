from __future__ import annotations
from typing import List, Type, Union, Dict, Callable, Tuple, TYPE_CHECKING

import os
import sys
import types
import logging
import fnmatch
import inspect
import pathlib
import functools
import importlib.util
from _balder.utils import get_class_that_defines_method
from _balder.setup import Setup
from _balder.device import Device
from _balder.feature import Feature
from _balder.vdevice import VDevice
from _balder.scenario import Scenario
from _balder.connection import Connection
from _balder.controllers import ScenarioController, SetupController, DeviceController, VDeviceController, \
    FeatureController, NormalScenarioSetupController
from _balder.exceptions import DuplicateForVDeviceError, UnknownVDeviceException
from _balder.utils import get_scenario_inheritance_list_of

if TYPE_CHECKING:
    from _balder.plugin_manager import PluginManager

logger = logging.getLogger(__file__)


class Collector:
    """
    The Collector class manages the loading and importing of all relevant balder objects. It does not resolve something,
    but secures that all relevant data is being collected.
    """
    # metadata object that contains all raw fixtures (classes that were not be resolved yet)
    raw_fixtures = {}

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

        self._all_py_files: Union[List[pathlib.Path], None] = None
        self._all_scenarios: Union[List[Type[Scenario]], None] = None
        self._all_setups: Union[List[Type[Setup]], None] = None
        self._all_connections: Union[List[Type[Connection]], None] = None

        self.balderglob_was_loaded = False

    @property
    def all_pyfiles(self) -> List[pathlib.Path]:
        """returns a list of all python files that were be found by the collector"""
        if self._all_py_files is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_py_files

    @property
    def all_scenarios(self) -> List[Type[Scenario]]:
        """returns a list of all scenarios that were found by the collector"""
        if self._all_scenarios is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_scenarios

    @property
    def all_setups(self) -> List[Type[Setup]]:
        """returns a list of all setups that were found by the collector"""
        if self._all_setups is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_setups

    @property
    def all_scenarios_and_setups(self) -> List[Union[Type[Scenario], Type[Setup]]]:
        """
        returns a list of all scenarios and setups that were found by the collector
        """
        new_list: List[Union[Type[Scenario], Type[Setup]]] = []
        new_list += self.all_scenarios
        new_list += self.all_setups
        return new_list

    @property
    def all_connections(self) -> List[Type[Connection]]:
        """returns a list of all connections that were found by the collector"""
        if self._all_connections is None:
            raise AttributeError("please call the `collect()` method before omitting this value")
        return self._all_connections

    def load_balderglob_py_file(self) -> Union[types.ModuleType, None]:
        """
        This method loads the global balderglob.py file and returns the module or None if the file does not exist.
        """
        filepath = self.working_dir.joinpath('balderglob.py')

        module_name = f"{self.working_dir.stem}.balderglob"

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

        for root, _, files in os.walk(str(self.working_dir)):
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
            if not cur_path.parts[-1].startswith('scenario_'):
                continue
            module_name = \
                f"{self.working_dir.stem}.{'.'.join(cur_path.parent.relative_to(self.working_dir).parts)}." \
                f"{ cur_path.stem}"

            if module_name in sys.modules.keys():
                # ignore all already imported items
                continue

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
                module_name = \
                    f"{self.working_dir.stem}.{'.'.join(cur_path.parent.relative_to(self.working_dir).parts)}." \
                    f"{cur_path.stem}"

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
        for _, cur_module in modules.items():
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
            if not cur_path.parts[-1].startswith('setup_'):
                continue
            module_name = \
                f"{self.working_dir.stem}.{'.'.join(cur_path.parent.relative_to(self.working_dir).parts)}." \
                f"{cur_path.stem}"

            # ignore all already imported items
            if module_name in sys.modules.keys():
                continue

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
            for cur_idx, cur_class in enumerate(base_classes):
                next_parent = None if cur_idx == 0 else base_classes[cur_idx - 1]
                if "IGNORE" in cur_class.__dict__.keys():
                    # IGNORE is mentioned in this specific class
                    if not isinstance(cur_class.IGNORE, list):
                        raise TypeError(f"the class attribute `{cur_class.__name__}.IGNORE` has to be from type list")
                    # check that all elements that are mentioned here exists in the parent's RUN, SKIP or IGNORE class
                    # variable or are defined in this class
                    for cur_ignore_method in cur_class.IGNORE:
                        if not inspect.ismethod(cur_ignore_method) or \
                                not cur_ignore_method.__name__.startswith('test_'):
                            raise TypeError(f"the given element {cur_ignore_method.__name__} for class attribute "
                                            f"`{cur_class.__name__}.IGNORE` is no valid test method")
                        if cur_ignore_method not in cur_class.__dict__.values() and next_parent is None or \
                                cur_ignore_method not in cur_class.__dict__.values() and next_parent is not None \
                                and cur_ignore_method not in next_parent.RUN + next_parent.SKIP + next_parent.IGNORE:
                            raise ValueError(f"the element `{cur_ignore_method.__name__}` given at class attribute "
                                             f"`{cur_class.__name__}.IGNORE` is not a test method of this scenario")
                else:
                    # IGNORE is not mentioned in this specific class -> so add an empty list for further access
                    cur_class.IGNORE = []
                if "SKIP" in cur_class.__dict__.keys():
                    # SKIP is mentioned in this specific class
                    if not isinstance(cur_class.SKIP, list):
                        raise TypeError(f"the class attribute `{cur_class.__name__}.SKIP` has to be from type list")
                    # check that all elements that are mentioned here exist in the parent's RUN or SKIP class variable
                    # or are defined in this class
                    for cur_skip_method in cur_class.SKIP:
                        if not inspect.ismethod(cur_skip_method) or \
                                not cur_skip_method.__name__.startswith('test_'):
                            raise TypeError(f"the given element {cur_skip_method.__name__} for class attribute "
                                            f"`{cur_class.__name__}.IGNORE` is no valid test method")
                        if cur_skip_method not in cur_class.__dict__.values():
                            if next_parent is None:
                                raise ValueError(f"the element `{cur_skip_method.__name__}` given at class attribute "
                                                 f"`{cur_class.__name__}.SKIP` is not a test method of this scenario")

                            if cur_skip_method in next_parent.IGNORE:
                                raise ValueError(f"the element `{cur_skip_method.__name__}` given at class "
                                                 f"attribute `{cur_class.__name__}.SKIP` was already added to "
                                                 f"IGNORE in a higher parent class - not possible to add it now to "
                                                 f"SKIP")

                            if cur_skip_method not in next_parent.SKIP and cur_skip_method not in next_parent.IGNORE:
                                raise ValueError(f"the element `{cur_skip_method.__name__}` given at class "
                                                 f"attribute `{cur_class.__name__}.SKIP` is not a test method of "
                                                 f"this scenario")
                else:
                    # SKIP is not mentioned in this specific class -> so add an empty list for further access
                    cur_class.SKIP = []
                if "RUN" in cur_class.__dict__.keys():
                    # RUN is mentioned in this specific class
                    if not isinstance(cur_class.RUN, list):
                        raise TypeError(f"the class attribute `{cur_class.__name__}.RUN` has to be from type list")
                    # check that all elements that are mentioned here exists in the parent's RUN class variable or are
                    # defined in this class
                    for cur_run_method in cur_class.RUN:
                        if not inspect.ismethod(cur_run_method) or \
                                not cur_run_method.__name__.startswith('test_'):
                            raise TypeError(f"the given element {cur_run_method.__name__} for class attribute "
                                            f"`{cur_class.__name__}.RUN` is no valid test method")
                        if cur_run_method not in cur_class.__dict__.values():
                            if next_parent is None:
                                raise ValueError(
                                    f"the element `{cur_run_method.__name__}` given at class attribute "
                                    f"`{cur_class.__name__}.RUN` is not a test method of this scenario")

                            if cur_run_method in next_parent.IGNORE:
                                raise ValueError(
                                    f"the element `{cur_run_method.__name__}` given at class attribute "
                                    f"`{cur_class.__name__}.RUN` was already added to IGNORE in a higher parent "
                                    f"class - not possible to add it now to RUN")
                            if cur_run_method in next_parent.SKIP:
                                raise ValueError(
                                    f"the element `{cur_run_method.__name__}` given at class attribute "
                                    f"`{cur_class.__name__}.RUN` was already added to SKIP in a higher parent "
                                    f"class - not possible to add it now to RUN")
                            if cur_run_method not in next_parent.RUN:
                                raise ValueError(
                                    f"the element `{cur_run_method.__name__}` given at class attribute "
                                    f"`{cur_class.__name__}.RUN` is not a test method of this scenario")
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
            owner_for_vdevice = owner_for_vdevice if owner_for_vdevice is not None else {}

            for cur_decorator_vdevice, cur_decorator_with_connections in cur_decorator_data_list:

                if owner is None:
                    raise TypeError("The use of the `@for_vdevice` decorator is only allowed for `Feature` objects and "
                                    "methods of `Feature` objects")
                if not issubclass(owner, Feature):
                    raise TypeError(f"The use of the `for_vdevice` decorator is not allowed for methods of a "
                                    f"`{owner.__name__}`. You should only use this decorator for `Feature` elements")

                if isinstance(cur_decorator_vdevice, str):
                    # vDevice is a string, so we have to convert it to the correct class
                    cur_decorator_vdevice = \
                        owner_feature_controller.get_inner_vdevice_class_by_string(cur_decorator_vdevice)

                    if cur_decorator_vdevice is None:
                        raise ValueError(f"can not find a matching inner VDevice class for the given vdevice string "
                                         f"`{cur_decorator_vdevice}` in the feature class `{owner.__name__}`")

                if cur_decorator_vdevice not in owner_feature_controller.get_abs_inner_vdevice_classes():
                    raise UnknownVDeviceException(f"the given vDevice `{cur_decorator_vdevice.__name__}` is not a "
                                                  f"usable vDevice in Feature class `{owner.__name__}`")

                if name not in owner_for_vdevice.keys():
                    owner_for_vdevice[name] = {}

                cur_decorator_cleaned_cnns = []
                for cur_cnn in cur_decorator_with_connections:
                    cur_cnn = cur_cnn() if isinstance(cur_cnn, type) and issubclass(cur_cnn, Connection) else cur_cnn
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

            def owner_wrapper(the_owner_of_this_method, the_name, wrap_fn):
                @functools.wraps(wrap_fn)
                def method_variation_multiplexer(this, *args, **kwargs):
                    controller = FeatureController.get_for(this.__class__)
                    if this.__class__ == the_owner_of_this_method:
                        # this is no parent class call -> use the set method-variation (set by VariationExecutor before)
                        _, _, func = controller.get_active_method_variation(the_name)
                    else:
                        func = controller.get_inherited_method_variation(the_owner_of_this_method, the_name)
                        if func is None:
                            raise AttributeError(f'there exists no method/method variation in class '
                                                 f'`{the_owner_of_this_method.__name__}` or its parent classes')
                    if len(args) == 0:
                        return func(self=this, **kwargs)

                    new_args = [this, *args]
                    return func(*new_args)

                return method_variation_multiplexer

            new_callback = owner_wrapper(owner, name, cur_fn)
            setattr(owner, name, new_callback)
            owner_feature_controller.set_method_based_for_vdevice(owner_for_vdevice)

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

    def _set_original_vdevice_in_features(self):
        """
        This method ensures that the original VDevice classes (that are defined in the :class:`Feature` classes) are
        saved inside their controllers.
        """
        for cur_feature in self.get_all_scenario_feature_classes() + self.get_all_setup_feature_classes():
            cur_feature_controller = FeatureController.get_for(cur_feature)
            cur_feature_controller.save_all_current_vdevice_references_as_originals()

    def _set_original_device_features(self):
        """
        This method ensures that the original features (that are instantiated in the
        :class:`Scenario`/:class:`Setup` devices or in the :class:`VDevice`) are saved inside their controllers.
        """

        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            cur_scenario_or_setup_controller = NormalScenarioSetupController.get_for(cur_scenario_or_setup)
            devices = cur_scenario_or_setup_controller.get_all_abs_inner_device_classes()
            for cur_device in devices:
                cur_device_controller = DeviceController.get_for(cur_device)
                cur_device_controller.save_all_original_instanced_features()

        for cur_feature in self.get_all_scenario_feature_classes() + self.get_all_setup_feature_classes():
            vdevices = FeatureController.get_for(cur_feature).get_abs_inner_vdevice_classes()
            for cur_vdevice in vdevices:
                cur_vdevice_controller = VDeviceController.get_for(cur_vdevice)
                cur_vdevice_controller.save_all_original_instanced_features()

    def _exchange_strings_with_objects(self):
        """
        This method exchanges all strings (that can be used in decorators) are exchanged with their real objects. It
        secures this for all :class:`Device` and :class:`VDevice` references inside the session.
        """
        # resolve connection Device strings (for all devices that are directly defined inside the scenario/setup)
        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            cur_scenario_or_setup_controller = NormalScenarioSetupController.get_for(cur_scenario_or_setup)
            for cur_device in cur_scenario_or_setup_controller.get_all_inner_device_classes():
                DeviceController.get_for(cur_device).resolve_connection_device_strings()

        # resolve connection VDevice strings (for all absolute devices of this scenario/setup)
        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            cur_scenario_or_setup_controller = NormalScenarioSetupController.get_for(cur_scenario_or_setup)
            for cur_device in cur_scenario_or_setup_controller.get_all_abs_inner_device_classes():
                DeviceController.get_for(cur_device).resolve_mapped_vdevice_strings()

    def _validate_scenario_and_setups(self):
        """
        This method validates that the inheritance of `Setup`/`Scenario` classes were being done correctly. It checks
        that all devices that are inherited has the same naming as their parents and also that every reused name (that
        is already be used for a device in parent class) does also inherit from the parent scenario/setup device.

        In addition to that, the method checks that either every device of higher class is defined (and overwritten) in
        the current class or non device
        """
        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            cur_scenario_or_setup_controller = NormalScenarioSetupController.get_for(cur_scenario_or_setup)
            cur_scenario_or_setup_controller.validate_inheritance()

    def _validate_features_and_their_vdevices(self):
        """
        This method validates the correct usage of features and their vDevices. It secures that the feature inheritance
        inside devices is correct and validates that inner referenced features inside other feature are correct. In
        addition to that it secures that inner vDevice classes of features are inherited and are used correctly.
        """
        all_features = self.get_all_scenario_feature_classes() + self.get_all_setup_feature_classes()
        all_devices = self.get_all_scenario_device_classes() + self.get_all_setup_device_classes()

        # validate inheritance for all features
        for cur_device in all_devices:
            DeviceController.get_for(cur_device).validate_inheritance_of_instantiated_features()

        # validate inner references of features inside features
        for cur_outer_device in all_devices:
            DeviceController.get_for(cur_outer_device).validate_inner_referenced_features()

        # validate all inner classes of all features and secure that Device subclasses are correctly used
        for cur_feature in all_features:
            FeatureController.get_for(cur_feature).validate_inner_classes()

        # validate that all parent VDevices are overwritten if one or more VDevice(s) are defined in current feature
        for cur_feature in all_features:
            cur_feature_controller = FeatureController.get_for(cur_feature)
            cur_feature_controller.validate_inner_vdevice_inheritance()

    def _determine_class_based_values_for_all_features(self, print_warning=True):
        """
        This method determines the absolute class based values for `@for_vdevice`. It will not update any internal
        values if the class-based-value was already set by an explicit class based `@for_vdevice` decorator. Otherwise,
        it determines the class based `@for_vdevice` value through analysing the method-based-decorators and sets this
        determined value. If the method finds a better value, it throws a warning with a suggestion for the (nicer)
        class based decorator.

        In both cases the method will secure that every given vDevice class is a real part of the current
        :class:`Feature` class (will be returned by direct call of method `Feature.get_inner_vdevice_classes()`).


        .. note::
            This method automatically updates the values for the parent classes, too. Every time it searches for the
            values it also considers the parent values for the vDevice or the parent class of the vDevice.
        """
        for cur_feature in self.get_all_scenario_feature_classes() + self.get_all_setup_feature_classes():
            cur_feature_controller = FeatureController.get_for(cur_feature)
            cur_feature_controller.determine_absolute_class_based_for_vdevice(print_warning)

    def _validate_vdevice_feature_references(self):
        """
        This method validates that VDevice references are used correctly.
        """
        # check feature (referenced from VDevice) exists in the related VDevice
        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            cur_scenario_or_setup_controller = NormalScenarioSetupController.get_for(cur_scenario_or_setup)
            cur_scenario_or_setup_controller.check_vdevice_feature_existence()

        # secure for all scenario features that the class based for_vdevice values of a child :class:`Feature` class
        # are contained_in the related VDevice defined in a parent :class:`Feature` class.
        for cur_feature in self.get_all_scenario_feature_classes():
            FeatureController.get_for(cur_feature).validate_inherited_class_based_vdevice_cnn_subset()

        # validates for every active class-based feature (only the ones that have an active VDevice<->Device mapping),
        # that a clear scenario-device-connection exists for this feature
        for cur_scenario in self.all_scenarios:
            ScenarioController.get_for(cur_scenario).validate_feature_clearance_for_parallel_connections()

    def _determine_absolute_device_connections(self):
        """
        This method manages the absolute connections for all collected :class:`Scenario` and :class:`Setup` objects. It
        determines the raw absolute connections for scenarios and setups and also creates the real device connections
        for all scenarios.
        """
        # determine the raw absolute device connections for all scenarios and setups
        for cur_scenario_or_setup in self.all_scenarios_and_setups:
            NormalScenarioSetupController.get_for(cur_scenario_or_setup).determine_raw_absolute_device_connections()

        # determine all absolute device connections (only for scenarios)
        for cur_scenario in self.all_scenarios:
            ScenarioController.get_for(cur_scenario).determine_absolute_device_connections()

    def _validate_feature_connections_in_setup(self):
        """
        This method validates that the connections of setup features are valid.
        It ensures, that every feature connection (that already has a vDevice<->Device mapping on setup level)
        has a connection that is CONTAINED-IN the connection between the related setup devices.
        """
        for cur_setup in self.all_setups:
            SetupController.get_for(cur_setup).validate_feature_possibility()

    def _filter_paths_after_allowed_paths(self, paths: List[pathlib.Path], filter_patterns: List[str]) \
            -> List[pathlib.Path]:
        """
        This method filters the given list of filepaths for the given filter_patterns. It returns a list with all
        remaining paths that are mathing the filter statements in `filter_paths`.

        Patterns are the same like for `fnmatch <https://docs.python.org/3/library/fnmatch.html#module-fnmatch>`_.

        :param paths: a list of all filepaths that should be filtered
        :param filter_patterns: a list of relative filter patterns that should be applied on the files of the classes
        :return: returns all classes of items that match any of the given patterns.
        """
        remaining = []

        for cur_pattern in filter_patterns:
            remaining += [cur_abs_path for cur_abs_path in paths
                          if fnmatch.fnmatch(str(cur_abs_path.relative_to(self.working_dir)), cur_pattern)]
        return list(set(remaining))


    def collect(self, plugin_manager: PluginManager, scenario_filter_patterns: Union[List[str], None],
                setup_filter_patterns: Union[List[str], None]):
        """
        This method manages the entire collection process.

        :param plugin_manager: contains the reference to the used plugin manager
        :param scenario_filter_patterns: a list with filter patterns for scenarios
        :param setup_filter_patterns: a list with filter patterns for setups
        """
        # load all py files
        self.load_balderglob_py_file()
        self._all_py_files = self.get_all_py_files()
        self._all_py_files = plugin_manager.execute_modify_collected_pyfiles(self._all_py_files)

        if scenario_filter_patterns:
            all_scenario_filepaths = self._filter_paths_after_allowed_paths(
                paths=self._all_py_files, filter_patterns=scenario_filter_patterns)
        else:
            all_scenario_filepaths = self._all_py_files
        if setup_filter_patterns:
            all_setup_filepaths = self._filter_paths_after_allowed_paths(
                paths=self._all_py_files, filter_patterns=setup_filter_patterns)
        else:
            all_setup_filepaths = self._all_py_files

        # collect all `Connection` classes (has to be first, because scenarios/setups can use them)
        self.load_all_connection_classes(py_file_paths=self._all_py_files)
        self._all_connections = self.get_all_connection_classes()

        # collect all `Scenario` classes
        self._all_scenarios = self.get_all_scenario_classes(py_file_paths=all_scenario_filepaths, filter_abstracts=True)
        # collect all `Setup` classes
        self._all_setups = self.get_all_setup_classes(py_file_paths=all_setup_filepaths, filter_abstracts=True)

        self._all_scenarios, self._all_setups = plugin_manager.execute_collected_classes(
            scenarios=self._all_scenarios, setups=self._all_setups)

        self._all_scenarios = Collector.filter_parent_classes_of(items=self._all_scenarios)
        self._all_setups = Collector.filter_parent_classes_of(items=self._all_setups)

        Collector.rework_method_variation_decorators()

        # do some further stuff after everything was read
        self._set_original_vdevice_in_features()
        self._set_original_device_features()
        self._exchange_strings_with_objects()

        # todo move this implementation in related controller
        self.set_run_skip_ignore_of_test_methods_in_scenarios()

        self._validate_scenario_and_setups()

        self._validate_features_and_their_vdevices()

        self._determine_class_based_values_for_all_features()

        self._validate_vdevice_feature_references()

        self._determine_absolute_device_connections()

        self._validate_feature_connections_in_setup()
