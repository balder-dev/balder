from __future__ import annotations
from typing import Type, Dict, Union, List, Callable, Tuple

import logging
import inspect
from _balder.vdevice import VDevice
from _balder.feature import Feature
from _balder.controllers import Controller
from _balder.controllers.vdevice_controller import VDeviceController
from _balder.connection import Connection
from _balder.exceptions import UnclearMethodVariationError, MultiInheritanceError, VDeviceOverwritingError, \
    VDeviceResolvingError, FeatureOverwritingError


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

        #: is a static member, that contains the **Class-Based-Binding** information for the related feature class
        #: sorted by feature types (will be automatically set by executor)
        self._cls_for_vdevice: Union[Dict[Type[VDevice], List[Connection, Type[Connection]]], None] = None

        #: contains the **Method-Based-Binding** information for the current feature type (will be automatically set by
        #: executor)
        self._for_vdevice: Union[Dict[str, Dict[Callable, Dict[Type[VDevice], List[Connection]]]], None] = None

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
        if self.get_class_based_for_vdevice() is not None:
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
                    if for_vdevice in vdevice_dict.keys():
                        for cur_cnn in vdevice_dict[for_vdevice]:
                            if isinstance(cur_cnn, type):
                                cur_cnn = cur_cnn()
                            # clean metadata here because this is no connection between real devices
                            cur_cnn.set_metadata_for_all_subitems(None)
                            intersection.append(cur_cnn)
        else:
            # there exists no method-variations
            if self.get_class_based_for_vdevice() is None:
                # there exists also no class based decorator -> set the gobal tree
                intersection.append(Connection())
        return intersection

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_class_based_for_vdevice(self) -> Union[Dict[Type[VDevice], List[Union[Connection]]], None]:
        """
        This method returns the class based data for the `@for_vdevice` decorator or None, if there is no decorator
        given
        """

        result = {}
        if self._cls_for_vdevice is not None:
            for cur_device, cnn_list in self._cls_for_vdevice.items():
                result[cur_device] = []
                for cur_cnn in cnn_list:
                    if isinstance(cur_cnn, type) and issubclass(cur_cnn, Connection):
                        result[cur_device].append(cur_cnn())
                    else:
                        result[cur_device].append(cur_cnn)
            return result

        return None

    def set_class_based_for_vdevice(
            self, data: Union[Dict[Type[VDevice], List[Union[Connection, Type[Connection]]]], None]):
        """
        This method allows to set the data of the class based `@for_vdevice` decorator.
        """
        self._cls_for_vdevice = data

    def get_absolute_class_based_for_vdevice(self, print_warning):
        """

        This method determines the absolute class based `@for_vdevice` value for the related feature.

        First it checks if there is a direct class based `@for_vdevice` decorator for this feature. It will not change
        anything, if the value was already set by an explicit class based `@for_vdevice` decorator. In this case the
        method only checks that every given vDevice class is a real part of the current :class:`Feature` class (will be
        returned by direct call of method `Feature.get_inner_vdevice_classes()`). Otherwise, it determines the class
        based `@for_vdevice` value through analysing of the method based decorators and sets this determined value. If
        the method has to determine the value, it throws a warning with a suggestion for a nice class based decorator.
        Also, here the method will analyse the given vDevice classes and secures that they are defined in the current :
        class:`Feature` class.

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
            FeatureController.get_for(next_parent_feat).get_absolute_class_based_for_vdevice(print_warning=False)

        # validate if all used vDevice references in method and class based `@for_vdevice` decorators can be used,
        # because they are members of this feature
        self._validate_vdevice_reference_used_in_for_vdevice_decorators()

        # now check if a definition for this class exists
        all_vdevices = self.get_abs_inner_vdevice_classes()

        cls_based_for_vdevice = self.get_class_based_for_vdevice()
        cls_based_for_vdevice = {} if cls_based_for_vdevice is None else cls_based_for_vdevice
        for cur_vdevice in all_vdevices:
            # determine the class based for_vdevice value only if there is no one defined for this vDevice
            if cur_vdevice in cls_based_for_vdevice.keys() and len(cls_based_for_vdevice[cur_vdevice]) > 0:
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
                    FeatureController.get_for(next_parent_feat).get_class_based_for_vdevice()
                next_parent_feat_cls_based_for_vdevice = {} if next_parent_feat_cls_based_for_vdevice is None else \
                    next_parent_feat_cls_based_for_vdevice
                if vdevice_of_interest in next_parent_feat_cls_based_for_vdevice.keys():
                    for cur_cnn in next_parent_feat_cls_based_for_vdevice[vdevice_of_interest]:
                        # clean metadata here because this is no connection between real devices
                        cur_cnn.set_metadata_for_all_subitems(None)
                        parent_values.append(cur_cnn)

            this_vdevice_intersection = parent_values

            # determine the class value automatically by discovering all method variations for this vDevice only
            this_vdevice_intersection += self._get_method_based_for_vdevice_intersection(for_vdevice=cur_vdevice)

            # set the determined data into the class based `@for_vdevice` class property
            cls_based_for_vdevice[cur_vdevice] = this_vdevice_intersection
            self.set_class_based_for_vdevice(cls_based_for_vdevice)

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

    def get_method_based_for_vdevice(self) -> \
            Union[Dict[str, Dict[Callable, Dict[Type[VDevice], List[Connection]]]], None]:
        """
        This method returns the method based data for the `@for_vdevice` decorator or None, if there is no decorator
        given
        """
        return self._for_vdevice

    def set_method_based_for_vdevice(
            self, data: Union[Dict[str, Dict[Callable, Dict[Type[VDevice], List[Connection]]]], None]):
        """
        This method allows to set the data for the method based `@for_vdevice` decorator.
        """
        self._for_vdevice = data

    def get_method_variation(
            self, of_method_name: str, for_vdevice: Type[VDevice],
            with_connection: Union[Connection, Tuple[Connection]], ignore_no_findings: bool = False) \
            -> Union[Callable, None]:
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

        all_vdevice_method_variations = self.get_method_based_for_vdevice()

        if isinstance(with_connection, tuple):
            with_connection = Connection.based_on(with_connection)

        if all_vdevice_method_variations is None:
            raise ValueError("the current feature has no method variations")
        if of_method_name not in all_vdevice_method_variations.keys():
            raise ValueError(f"can not find the method `{of_method_name}` in method variation data dictionary")

        # first determine all possible method-variations
        all_possible_method_variations = {}
        for cur_impl_method, cur_method_impl_dict in self.get_method_based_for_vdevice()[of_method_name].items():
            if for_vdevice in cur_method_impl_dict.keys():
                cur_impl_method_cnns = []
                for cur_cnn in cur_method_impl_dict[for_vdevice]:
                    cur_impl_method_cnns += cur_cnn.get_singles()
                for cur_single_impl_method_cnn in cur_impl_method_cnns:
                    if cur_single_impl_method_cnn.contained_in(with_connection, ignore_metadata=True):
                        # this variation is possible
                        # ADD IT if it is not available yet
                        if cur_impl_method not in all_possible_method_variations.keys():
                            all_possible_method_variations[cur_impl_method] = cur_single_impl_method_cnn
                        # COMBINE IT if it is already available
                        else:
                            all_possible_method_variations[cur_impl_method] = Connection.based_on(
                                all_possible_method_variations[cur_impl_method], cur_single_impl_method_cnn)

        # if there are more than one possible method variation, try to sort them hierarchical
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

        if len(all_possible_method_variations) == 1:
            return list(all_possible_method_variations.keys())[0]

        # we have to determine the outer one
        length_before = None
        while length_before is None or length_before != len(all_possible_method_variations):
            length_before = len(all_possible_method_variations)
            for cur_meth, cur_cnn in all_possible_method_variations.items():
                can_be_deleted = True
                for _, cur_other_cnn in all_possible_method_variations.items():
                    if cur_cnn == cur_other_cnn:
                        continue
                    if not cur_cnn.contained_in(cur_other_cnn):
                        can_be_deleted = False
                if can_be_deleted:
                    del all_possible_method_variations[cur_meth]
                    break
            if len(all_possible_method_variations) == 1:
                # done
                break

        if len(all_possible_method_variations) > 1:
            raise UnclearMethodVariationError(
                f"found more than one possible method variation for method "
                f"`{self.related_cls.__name__}.{of_method_name}` with vDevice `{for_vdevice.__name__}` "
                f"and usable connection `{with_connection.get_tree_str()}´")
        return list(all_possible_method_variations.keys())[0]

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
            outer_class_name, _ = cur_class.__qualname__.split('.')[-2:]
            if outer_class_name != self.related_cls.__name__:
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
            cur_vdevice_cls_cnn = self.get_class_based_for_vdevice().get(cur_vdevice)
            # get parent class of vdevice
            relevant_parent_class = None
            for cur_vdevice_base_cls in cur_vdevice.__bases__:
                if issubclass(cur_vdevice_base_cls, VDevice) and cur_vdevice_base_cls != VDevice:
                    relevant_parent_class = cur_vdevice_base_cls
                    relevant_parent_class_controller = VDeviceController.get_for(relevant_parent_class)
                    while relevant_parent_class != VDevice and \
                            relevant_parent_class_controller.get_outer_class() == self.related_cls:
                        for cur_vdevice_base_of_base_cls in relevant_parent_class.__bases__:
                            if issubclass(cur_vdevice_base_of_base_cls, VDevice):
                                relevant_parent_class = cur_vdevice_base_of_base_cls
                                if relevant_parent_class == VDevice:
                                    break
                                if relevant_parent_class_controller.get_outer_class() != self.related_cls:
                                    # found next vDevice in another Feature
                                    break
                    if relevant_parent_class != VDevice:
                        break
            if relevant_parent_class is not None and relevant_parent_class != VDevice:
                relevant_parent_class_controller = VDeviceController.get_for(relevant_parent_class)
                # only if there is a higher class which has to be considered
                parent_vdevice_feature = relevant_parent_class_controller.get_outer_class()
                if parent_vdevice_feature not in to_checking_parent_features:
                    to_checking_parent_features.append(parent_vdevice_feature)
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
