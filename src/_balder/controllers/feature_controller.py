from __future__ import annotations

import copy
from typing import Type, Dict, Union, List, Callable, Tuple

import logging
import inspect
from _balder.cnnrelations import OrConnectionRelation
from _balder.device import Device
from _balder.vdevice import VDevice
from _balder.feature import Feature
from _balder.controllers import Controller
from _balder.controllers.vdevice_controller import VDeviceController
from _balder.connection import Connection
from _balder.exceptions import UnclearMethodVariationError, MultiInheritanceError, VDeviceOverwritingError, \
    VDeviceResolvingError, FeatureOverwritingError, IllegalVDeviceMappingError

logger = logging.getLogger(__file__)


class FeatureController(Controller):
    """
    This is the controller class for :class:`Feature` items.
    """
    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing feature and its corresponding controller object
    _items: Dict[Type[Feature], FeatureController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != FeatureController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`FeatureController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Feature):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Feature.__name__}`')
        if related_cls == Feature:
            raise TypeError(f'the attribute `related_cls` is `{Feature.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

        #: holds the defined **Class-Based-Binding** for the related feature class sorted by VDevice types
        self._cls_for_vdevice: Dict[Type[VDevice], Connection] = {}

        #: holds the absolute calculated **Class-Based-Binding** for the related feature class sorted by VDevice types
        #: (will be calculated by :meth:`FeatureController.determine_absolute_class_based_for_vdevice`, which will be
        #: called during collecting)
        self._abs_cls_for_vdevice: Union[Dict[Type[VDevice], Connection], None] = None

        #: contains the **Method-Based-Binding** information for the current feature type (will be automatically set by
        #: executor)
        self._for_vdevice: Union[Dict[str, Dict[Callable, Dict[Type[VDevice], Connection]]], None] = None

        #: contains the original defined :class:`VDevice` objects for this feature (will be automatically set by
        #:  :class:`Collector`)
        self._original_vdevice_definitions: Union[Dict[str, Type[VDevice]], None] = None

        #: contains the current active method variations for the related feature class - for every key (method name str)
        #: a tuple with the VDevice type, the valid connection and the callable itself will be returned
        self._current_active_method_variation: Dict[str, Tuple[Type[VDevice], Connection, Callable]] = {}

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Feature]) -> FeatureController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if FeatureController._items.get(related_cls) is None:
            item = FeatureController(related_cls, _priv_instantiate_key=FeatureController.__priv_instantiate_key)
            FeatureController._items[related_cls] = item

        return FeatureController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Feature]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _validate_vdevice_reference_used_in_for_vdevice_decorators(self):
        # now check if a definition for this class exists
        all_vdevices = self.get_abs_inner_vdevice_classes()
        # check the class based @for_vdevice and check the used vDevice classes here
        for cur_decorated_vdevice in self.get_class_based_for_vdevice().keys():
            if cur_decorated_vdevice not in all_vdevices:
                raise VDeviceResolvingError(
                    f"you assign a vDevice to the class based decorator `@for_vdevice()` of the feature class "
                    f"`{self.related_cls.__name__}` which is no direct member of this feature - note that you have "
                    f"to define the vDevice in your feature before using it in the decorator - if necessary "
                    f"overwrite it")
        # check the method based @for_vdevice and check the used vDevice classes here
        if self.get_method_based_for_vdevice() is not None:
            for cur_method_name, cur_method_data in self.get_method_based_for_vdevice().items():
                for _, vdevice_dict in cur_method_data.items():
                    for cur_vdevice in vdevice_dict.keys():
                        if cur_vdevice not in all_vdevices:
                            raise VDeviceResolvingError(
                                f"you assign a vDevice to the method variation `{cur_method_name}` of the feature "
                                f"class `{self.related_cls.__name__}` which is no direct member of this feature - note "
                                f"that you have to use the overwritten version if you overwrite a vDevice")

    def _get_method_based_for_vdevice_intersection(self, for_vdevice) -> List[Connection]:
        """helper method that determines the intersection connection list of all method based `@for_vdevice`
        connections of the given `for_vdevice`"""
        intersection = []

        if self.get_method_based_for_vdevice() is not None:
            for _, method_dict in self.get_method_based_for_vdevice().items():
                for _, vdevice_dict in method_dict.items():
                    if for_vdevice not in vdevice_dict.keys():
                        continue
                    for cur_cnn in vdevice_dict[for_vdevice]:
                        if isinstance(cur_cnn, type):
                            cur_cnn = cur_cnn()
                        # clean metadata here because this is no connection between real devices
                        cur_cnn.set_metadata_for_all_subitems(None)
                        intersection.append(cur_cnn)
        if len(intersection) == 0:
            return [Connection()]
        return intersection

    def _determine_all_theoretically_unordered_method_variations(
            self, of_method_name: str, for_vdevice: Type[VDevice],
            with_connection: Union[Connection, Tuple[Connection]]) -> Dict[Callable, Connection]:
        """
        This method returns all theoretically matching method variations. It returns more than one, if there are
        multiple method variation for the given VDevice in this feature, where the given connection is part of the
        connection described by the method variation.

        :param of_method_name: the name of the method that should be returned
        :param for_vdevice: the VDevice that is mapped
        :param with_connection: the connection that is used between the device that uses the related feature and the
                                VDevice
        :return: a dictionary that holds all available method variation that matches here
        """
        all_vdevice_method_variations = self.get_method_based_for_vdevice()

        if all_vdevice_method_variations is None:
            raise ValueError("the current feature has no method variations")

        if of_method_name not in all_vdevice_method_variations.keys():
            raise ValueError(f"can not find the method `{of_method_name}` in method variation data dictionary")

        all_possible_method_variations = {}
        for cur_impl_method, cur_method_impl_dict in all_vdevice_method_variations[of_method_name].items():
            if for_vdevice in cur_method_impl_dict.keys():
                cur_impl_method_cnns = cur_method_impl_dict[for_vdevice].get_singles()
                for cur_single_impl_method_cnn in cur_impl_method_cnns:
                    if cur_single_impl_method_cnn.contained_in(with_connection, ignore_metadata=True):
                        # this variation is possible
                        # ADD IT if it is not available yet
                        if cur_impl_method not in all_possible_method_variations.keys():
                            all_possible_method_variations[cur_impl_method] = cur_single_impl_method_cnn
                        # COMBINE IT if it is already available
                        else:
                            all_possible_method_variations[cur_impl_method] = Connection.based_on(
                                OrConnectionRelation(all_possible_method_variations[cur_impl_method],
                                                     cur_single_impl_method_cnn))
        return all_possible_method_variations

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_class_based_for_vdevice(self) -> Dict[Type[VDevice], Connection]:
        """
        This method returns the class based data for the `@for_vdevice` decorator.
        """
        return copy.copy(self._cls_for_vdevice)

    def get_abs_class_based_for_vdevice(self) -> Dict[Type[VDevice], Connection]:
        """
        This method returns the absolute calculated class-based-for-vdevice data for this feature.
        """
        if self._abs_cls_for_vdevice is None:
            raise RuntimeError('can not access the absolute class based for-vdevices because they are not set yet')
        return self._abs_cls_for_vdevice

    def set_class_based_for_vdevice(self, data: Dict[Type[VDevice], Connection]):
        """
        This method allows to set the data of the class based `@for_vdevice` decorator.
        """
        self._cls_for_vdevice = data

    def determine_absolute_class_based_for_vdevice(self, print_warning):
        """

        This method determines the absolute class based `@for_vdevice` value for the related feature.

        First it checks if there is a direct class based `@for_vdevice` decorator for this feature. It will not change
        anything, if the value was already set by an explicit class based `@for_vdevice` decorator. In this case the
        method only checks that every given vDevice class is a real part of the current :class:`Feature` class (will be
        returned by direct call of method `Feature.get_inner_vdevice_classes()`). Otherwise, it determines the class
        based `@for_vdevice` value through analysing of the method based decorators and sets this determined value. If
        the method has to determine the value, it throws a warning with a suggestion for a nice class based decorator.
        Also, here the method will analyse the given vDevice classes and secures that they are defined in the current
        :class:`Feature` class.

        .. note::
            This method automatically updates the values for the parent classes, too. Every time it searches for the
            values it considers the parent values for the vDevice or the parent class of the vDevice, too.

        .. note::
            This method can throw a user warning (`throw_warning` has to be True for that), but only on the given list
            of :class:`Feature` classes. All parent :class:`Feature` classes will be determined correctly, but will not
            throw a waring.
        """
        # first determine this for all parent classes
        next_parent_feat = self.get_next_parent_feature()
        # with the following recursive call we guarantee that the next parent class has the correct resolved class
        #  based @for_vdevice information
        if next_parent_feat:
            FeatureController.get_for(next_parent_feat).determine_absolute_class_based_for_vdevice(print_warning=False)

        # validate if all used vDevice references in method and class based `@for_vdevice` decorators can be used,
        # because they are members of this feature
        self._validate_vdevice_reference_used_in_for_vdevice_decorators()

        # now check if a definition for this class exists
        all_vdevices = self.get_abs_inner_vdevice_classes()

        cls_based_for_vdevice = self.get_class_based_for_vdevice()
        for cur_vdevice in all_vdevices:
            # determine the class based for_vdevice value only if there is no one defined for this vDevice
            if cur_vdevice in cls_based_for_vdevice.keys():
                # there already exists a definition for this vDevice -> IGNORE
                continue

            # first determine the valid parent intersection (can also be extended itself)

            # get the correct vDevice that is known in the parent feature class
            vdevice_controller = VDeviceController.get_for(cur_vdevice)
            if vdevice_controller.get_outer_class() == self.related_cls:
                # this cur_vdevice is defined in this Feature class -> check if a parent class of it exists in
                # parent classes of this feature
                #  -> search parent vDevice existence and check if this vDevice is also used in a parent class of
                #     this feature
                #  -> if it does not exist -> there is no parent class based definition
                vdevice_of_interest = vdevice_controller.get_next_parent_vdevice()

            else:
                # the definition scope of the VDevice is in a higher Feature parent -> has to be in the
                # `__cls_for_vdevice` in one of the next base classes
                vdevice_of_interest = cur_vdevice

            parent_values = []
            # read vDevice connection tree of parent feature class (only if the vDevice already exists in the
            # parent class)
            if vdevice_of_interest is not None and next_parent_feat is not None:
                next_parent_feat_cls_based_for_vdevice = \
                    FeatureController.get_for(next_parent_feat).get_abs_class_based_for_vdevice()
                if vdevice_of_interest in next_parent_feat_cls_based_for_vdevice.keys():
                    cnn = next_parent_feat_cls_based_for_vdevice[vdevice_of_interest]
                    # clean metadata here because this is no connection between real devices
                    cnn.set_metadata_for_all_subitems(None)
                    parent_values.append(cnn)

            this_vdevice_intersection = parent_values

            # determine the class value automatically by discovering all method variations for this vDevice only
            this_vdevice_intersection += self._get_method_based_for_vdevice_intersection(for_vdevice=cur_vdevice)

            # print warning only if the printing is enabled and there is a sub connection tree (otherwise, the
            #  decorator is not necessary)
            if print_warning and len(this_vdevice_intersection) > 0:
                # only print the warning if there exists method variations for the feature
                if self.get_method_based_for_vdevice() is not None:
                    logger.warning(
                        f"your used feature class `{self.related_cls.__name__}` doesn't provide a class based "
                        f"@for_vdevice decorator for the vDevice `{cur_vdevice.__name__}`\n"
                        f"Balder has determined a possible marker:\n\n"
                        f'@balder.for_vdevice("{cur_vdevice.__name__}", '
                        f'{", ".join([cur_cnn.get_tree_str() for cur_cnn in this_vdevice_intersection])})\n\n')

            # set the determined data into the class based `@for_vdevice` class property
            cls_based_for_vdevice[cur_vdevice] = Connection.based_on(OrConnectionRelation(*this_vdevice_intersection))

        self._abs_cls_for_vdevice = cls_based_for_vdevice

    def get_method_based_for_vdevice(self) -> \
            Union[Dict[str, Dict[Callable, Dict[Type[VDevice], Connection]]], None]:
        """
        This method returns the method based data for the `@for_vdevice` decorator or None, if there is no decorator
        given
        """
        return self._for_vdevice

    def set_method_based_for_vdevice(
            self, data: Union[Dict[str, Dict[Callable, Dict[Type[VDevice], Connection]]], None]):
        """
        This method allows to set the data for the method based `@for_vdevice` decorator.
        """
        self._for_vdevice = data

    def get_method_variation(
            self,
            of_method_name: str,
            for_vdevice: Type[VDevice],
            with_connection: Connection,
            ignore_no_findings: bool = False
    ) -> Union[Callable, None]:
        """
        This method searches for the unique possible method variation and returns it. In its search, the method also
        includes the parent classes of the related feature element of this controller.

        .. note::
            The method throws an exception if it can not find a valid unique method variation for the given data.

        .. note::
            Note, that the method does not check if the method name, the VDevice nor the given `connection` is really a
            part of this object. Please secure that the data is validated before.

        .. note::
            The method determines all possible method-variations. If it finds more than one clear method variation it
            tries to sort them hierarchical. This is done by checking if one possible method variation is contained in
            the other. If this can be clearly done, the method returns the furthest out one. Otherwise, it throws an
            `UnclearMethodVariationError`

        :param of_method_name: the name of the method that should be returned

        :param for_vdevice: the VDevice that is mapped

        :param with_connection: the connection that is used between the device that uses the related feature and the
                                VDevice

        :param ignore_no_findings: if this attribute is true, the method will not throw an exception if it can not find
                                   something, it only returns None

        :return: the method variation callable for the given data (or none, if the method does not exist in this object
                 or in a parent class of it)
        """
        # first determine all possible method-variations
        all_possible_method_variations = self._determine_all_theoretically_unordered_method_variations(
            of_method_name=of_method_name, for_vdevice=for_vdevice, with_connection=with_connection)

        # there are no method variations in this feature directly -> check parent classes
        if len(all_possible_method_variations) == 0:
            # try to execute this method in parent classes
            for cur_base in self.related_cls.__bases__:
                if issubclass(cur_base, Feature) and cur_base != Feature:
                    parent_meth_result = FeatureController.get_for(cur_base).get_method_variation(
                        of_method_name=of_method_name, for_vdevice=for_vdevice, with_connection=with_connection,
                        ignore_no_findings=True)
                    if parent_meth_result:
                        return parent_meth_result
            if not ignore_no_findings:
                raise UnclearMethodVariationError(
                    f"found no possible method variation for method "
                    f"`{self.related_cls.__name__}.{of_method_name}` with vDevice `{for_vdevice.__name__}` "
                    f"and usable connection `{with_connection.get_tree_str()}´")
            return None

        # we only have one -> selection is clear
        if len(all_possible_method_variations) == 1:
            return list(all_possible_method_variations.keys())[0]

        # if there are more than one possible method variation, try to determine the outer one
        remaining_possible_method_variations = list(
            filter(
                lambda meth: not max(all_possible_method_variations[meth].contained_in(cur_other_cnn)
                                     for cur_other_cnn in all_possible_method_variations.values()
                                     if cur_other_cnn != all_possible_method_variations[meth]),
                all_possible_method_variations.keys())
        )

        if len(remaining_possible_method_variations) > 1:
            raise UnclearMethodVariationError(
                f"found more than one possible method variation for method "
                f"`{self.related_cls.__name__}.{of_method_name}` with vDevice `{for_vdevice.__name__}` "
                f"and usable connection `{with_connection.get_tree_str()}´")
        return remaining_possible_method_variations[0]

    def get_inner_vdevice_classes(self) -> List[Type[VDevice]]:
        """
        This is a method that determines the inner VDevice classes for the related feature class. If the method can not
        find some VDevices in the current class it returns an empty list. This method will never search in parent
        classes.

        If you want to get the absolute VDevices use :meth:`Feature.get_inner_vdevice_classes`.
        """

        all_classes = inspect.getmembers(self.related_cls, inspect.isclass)
        filtered_classes = []
        for _, cur_class in all_classes:
            if not issubclass(cur_class, VDevice):
                # filter all classes and make sure that only the child classes of :class:`VDevice` remain
                continue

            if VDeviceController.get_for(cur_class).get_outer_class() != self.related_cls:
                # filter all classes that do not match the setup name in __qualname__
                continue
            # otherwise, add this candidate
            filtered_classes.append(cur_class)

        if len(filtered_classes) == 0:
            # do not found some VDevice classes -> search in parent
            for cur_base in self.related_cls.__bases__:
                if cur_base == Feature:
                    return []
                if issubclass(cur_base, Feature):
                    return FeatureController.get_for(cur_base).get_abs_inner_vdevice_classes()

        return filtered_classes

    def get_inner_vdevice_class_by_string(self, device_str: str) -> Union[Type[VDevice], None]:
        """
        This method returns the inner VDevice class for the given string.

        :param device_str: the name string of the VDevice that should be returned

        :return: the VDevice class or None, if the method has not found any class with this name
        """
        possible_vdevs = [cur_vdevice for cur_vdevice in self.get_inner_vdevice_classes()
                          if cur_vdevice.__name__ == device_str]
        if len(possible_vdevs) == 0:
            return None
        if len(possible_vdevs) > 1:
            raise RuntimeError("found more than one possible vDevices - something unexpected happened")

        return possible_vdevs[0]

    def get_abs_inner_vdevice_classes(self) -> List[Type[VDevice]]:
        """
        This is a method that determines the inner VDevice classes for the feature class. If the method can not find
        some VDevices in the related feature class it also starts searching in the base classes. It always returns the
        first existing definition in the relevant parent classes.
        """

        filtered_classes = self.get_inner_vdevice_classes()

        if len(filtered_classes) == 0:
            # do not found some VDevice classes -> search in parent
            for cur_base in self.related_cls.__bases__:
                if cur_base == Feature:
                    return []
                if issubclass(cur_base, Feature):
                    return FeatureController.get_for(cur_base).get_abs_inner_vdevice_classes()

        return filtered_classes

    def get_inner_referenced_features(self) -> Dict[str, Feature]:
        """
        This method returns a dictionary with all referenced :class:`Feature` objects, where the variable name is the
        key and the instantiated object the value.
        """

        result = {}
        for cur_name in dir(self.related_cls):
            cur_val = getattr(self.related_cls, cur_name)
            if isinstance(cur_val, Feature):
                result[cur_name] = cur_val
        return result

    def validate_inner_vdevice_inheritance(self):
        """
        This method validates the inheritance of all inner :class:`VDevice` classes of the feature that belongs to this
        controller.

        It secures that new :class:`VDevice` classes are added or existing :class:`VDevice` classes are completely being
        overwritten for every feature level. The method only allows the overwriting of :class:`VDevices`, which are
        subclasses of another :class:`VDevice` that is defined in a parent :class:`Feature` class. In addition, the
        class has to have the same name as its parent class.

        The method also secures that the user overwrites instantiated :class:`Feature` classes in the VDevice (class
        property name is the same) only with subclasses of the element that is being overwritten. New Features can be
        added without consequences.
        """

        all_direct_vdevices_of_this_feature_lvl = self.get_inner_vdevice_classes()
        if len(all_direct_vdevices_of_this_feature_lvl) != 0:
            # check that all absolute items of higher class are implemented
            next_feature_parent = None
            for cur_parent in self._related_cls.__bases__:
                if issubclass(cur_parent, Feature) and cur_parent != Feature:
                    if next_feature_parent is not None:
                        raise MultiInheritanceError(
                            "can not select the next parent class, found more than one parent classes for feature "
                            f"`{self._related_cls.__name__}` that is a subclass of `{Feature.__name__}`")
                    next_feature_parent = cur_parent
            # only continue if the current feature has a parent class
            if next_feature_parent:
                # first check the parent feature (secure that the inheritance chain is valid first)
                parent_collector = FeatureController.get_for(next_feature_parent)
                parent_collector.validate_inner_vdevice_inheritance()

                # now continue with checking the inheritance between this feature and its direct parent
                parent_vdevices = parent_collector.get_abs_inner_vdevice_classes()
                # now check that every parent vDevice also exists in the current selection
                for cur_parent_vdevice in parent_vdevices:
                    direct_namings = [cur_item.__name__ for cur_item in all_direct_vdevices_of_this_feature_lvl]
                    # check that the parent vDevice exists in the direct namings
                    if cur_parent_vdevice.__name__ not in direct_namings:
                        raise VDeviceOverwritingError(
                            f"missing overwriting of parent VDevice class `{cur_parent_vdevice.__qualname__}` in "
                            f"feature class `{self._related_cls.__name__}` - if you overwrite one or more VDevice(s) "
                            f"you have to overwrite all!")

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

    def validate_inherited_class_based_vdevice_cnn_subset(self):
        """
        This method checks that the class based for_vdevice values of a child :class:`Feature` class are contained_in
        the related VDevice defined in a parent :class:`Feature` class.
        """

        to_checking_parent_features = []

        feature_vdevices = self.get_abs_inner_vdevice_classes()
        for cur_vdevice in feature_vdevices:
            cur_vdevice_cls_cnn = self.get_abs_class_based_for_vdevice().get(cur_vdevice)
            # get parent class of vdevice
            relevant_parent_class = VDeviceController.get_for(cur_vdevice).get_next_parent_vdevice()

            # continue with next vdevice if no relevant parent class was found
            if relevant_parent_class is None:
                continue

            relevant_parent_class_controller = VDeviceController.get_for(relevant_parent_class)
            # only if there is a higher class which has to be considered
            parent_vdevice_feature = relevant_parent_class_controller.get_outer_class()
            if parent_vdevice_feature not in to_checking_parent_features:
                to_checking_parent_features.append(parent_vdevice_feature)
            parent_vdevice_cnn = \
                FeatureController.get_for(
                    parent_vdevice_feature).get_abs_class_based_for_vdevice()[relevant_parent_class]
            # check if VDevice connection elements are all contained in the parent connection
            if not cur_vdevice_cls_cnn.contained_in(parent_vdevice_cnn, ignore_metadata=True):
                raise VDeviceResolvingError(
                    f"the VDevice `{cur_vdevice.__name__}` is a child of the VDevice "
                    f"`{relevant_parent_class.__name__}`, which doesn't implements the connection of "
                    f"the child - the connection element `{cur_vdevice_cls_cnn.get_tree_str()})´ is not "
                    f"contained in the connection-tree of the parent VDevice")

        # validate inheritance levels for all features with parent VDevices as inner-classes
        for cur_feature in to_checking_parent_features:
            FeatureController.get_for(cur_feature).validate_inherited_class_based_vdevice_cnn_subset()

    def get_next_parent_feature(self) -> Union[Type[Feature], None]:
        """
        This method returns the next parent class of this feature, which is still a subclass of :class:`Feature`. If
        the next parent class is :class:`Feature`, None will be returned.

        :return: the parent Feature class or None if no parent exists
        """
        possible_parent_classes = []
        for cur_parent in self.related_cls.__bases__:
            if issubclass(cur_parent, Feature) and cur_parent != Feature:
                possible_parent_classes.append(cur_parent)

        if len(possible_parent_classes) > 1:
            raise MultiInheritanceError(
                f"the feature `{self.related_cls.__name__}` has more than one parent classes from type "
                f"`Feature` - this is not allowed")

        if len(possible_parent_classes) == 1:
            # we have found one parent feature class
            return possible_parent_classes[0]

        # we have no parent class
        return None

    def set_active_method_variation(self, method_selection: Dict[str, Tuple[Type[VDevice], Connection, Callable]]):
        """
        This method sets the active method variation selection for the related feature class.
        :param method_selection: the method selection that should be set
        """
        self._current_active_method_variation = method_selection

    def get_active_method_variation(self, method_name: str) \
            -> Union[Tuple[Type[VDevice], Connection, Callable], Tuple[None, None, None]]:
        """
        This method returns the current active method variation for the given `method_name` for the related fixture.

        .. note::
            Please note, this method only returns the set active method variation for this related feature only. It does
            not check parent classes of this feature.

        :param method_name: the name of the method the current active method variation should be returned

        :return: a tuple with the current active method selection or a tuple with `None` if no active method variation
                 exists on this feature class level
        """
        return self._current_active_method_variation.get(method_name, tuple([None, None, None]))

    def get_inherited_method_variation(self, parent_class: Type[Feature], method_var_name: str):
        """
        This method will determine the correct inherited method-variation for the current object. For this, it searches
        in the base classes of the given `parent_class` (which has to be a parent class of `self`) for the
        method-variation that should be called.
        It automatically detects if the parent class has a method-variation or is a single normal method. In case that
        the method is a single normal method, it will directly return it, otherwise it searches the correct
        method-variation according to the vDevice mapping of the current object and return the current active
        method-variation.

        :param parent_class: the parent class of this object, the method should start searching for the
                             `method_var_name` method (it searches in this class and all parents)

        :param method_var_name: the name of the method or of the method variation that should be returned
        """

        parent_class_controller = FeatureController.get_for(parent_class)
        if parent_class_controller.get_method_based_for_vdevice() is not None and \
                method_var_name in parent_class_controller.get_method_based_for_vdevice().keys():
            # the parent class has a method-variation -> get the current active version of it

            # first get the active data for the instantiated feature object
            active_vdevice, active_cnn_intersection, _ = self.get_active_method_variation(method_var_name)
            # get the vDevice object that is used in the given parent class
            if hasattr(parent_class, active_vdevice.__name__):
                parent_vdevice = getattr(parent_class, active_vdevice.__name__)
            else:
                return None

            # then determine the correct method variation according to the data of the instantiated object
            cur_method_variation = parent_class_controller.get_method_variation(
                of_method_name=method_var_name, for_vdevice=parent_vdevice,
                with_connection=active_cnn_intersection, ignore_no_findings=True)
            return cur_method_variation

        if hasattr(parent_class, method_var_name):
            # we found one normal method in this object
            return getattr(parent_class, method_var_name)

        # execute this method for all based and check if there is exactly one
        next_base_feature_class = parent_class_controller.get_next_parent_feature()
        if next_base_feature_class is None:
            return None

        return self.get_inherited_method_variation(next_base_feature_class, method_var_name)

    def validate_inner_classes(self):
        """
        This method validates all inner classes of the related feature and secures that none of these subclasses are
        subclass of :class:`Device` but not subclasses from :class:`VDevice`. Of course other inner-classes that are not
        required for balder are allowed too.
        """
        all_inner_classes = inspect.getmembers(self.related_cls, inspect.isclass)
        for cur_inner_name, cur_inner_class in all_inner_classes:
            if not issubclass(cur_inner_class, Device):
                # ignore this element
                continue
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
                        f"vDevice `{cur_inner_class.__name__}` of feature `{self.related_cls.__name__}` "
                        f"has a own vDevice mapping - vDevice mappings are allowed for features on Devices "
                        f"only")

    def get_original_vdevice_definitions(self) -> Dict[str, Type[VDevice]]:
        """
        This method returns the :class:`VDevice` definitions that are the original definitions for this feature.
        """
        if self._original_vdevice_definitions is None:
            raise RuntimeError('can not access the original VDevice definitions before they were set with '
                               '`save_all_current_vdevice_references_as_originals`')
        return self._original_vdevice_definitions

    def save_all_current_vdevice_references_as_originals(self):
        """
        This method saves the current existing :class:`VDevice` definitions inside this feature as originals.
        """
        new_originals = self.get_abs_inner_vdevice_classes()
        self._original_vdevice_definitions = {cur_vdevice.__name__: cur_vdevice for cur_vdevice in new_originals}
