from __future__ import annotations

import logging
from typing import Type, Dict, Union, List, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.connection import Connection
    from _balder.vdevice import VDevice
    from _balder.feature import Feature

import inspect
from _balder.controllers import Controller
from _balder.exceptions import UnclearMethodVariationError


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
        from _balder.feature import Feature

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

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_class_based_for_vdevice(self) -> Union[Dict[Type[VDevice], List[Union[Connection]]], None]:
        """
        This method returns the class based data for the `@for_vdevice` decorator or None, if there is no decorator
        given
        """
        from _balder.connection import Connection

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
        else:
            return None

    def set_class_based_for_vdevice(
            self, data: Union[Dict[Type[VDevice], List[Union[Connection, Type[Connection]]]], None]):
        """
        This method allows to set the data of the class based `@for_vdevice` decorator.
        """
        self._cls_for_vdevice = data

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
        from balder import Connection

        all_vdevice_method_variations = self.get_method_based_for_vdevice()

        if isinstance(with_connection, tuple):
            with_connection = Connection.based_on(with_connection)

        if all_vdevice_method_variations is None:
            raise ValueError(f"the current feature has no method variations")
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
        elif len(all_possible_method_variations) == 1:
            return list(all_possible_method_variations.keys())[0]
        else:
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
        from _balder.vdevice import VDevice
        from _balder.feature import Feature

        all_classes = inspect.getmembers(self.related_cls, inspect.isclass)
        filtered_classes = []
        for _, cur_class in all_classes:
            if not issubclass(cur_class, VDevice):
                # filter all classes and make sure that only the child classes of :class:`VDevice` remain
                continue
            outer_class_name, device_class_name = cur_class.__qualname__.split('.')[-2:]
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
        from _balder.feature import Feature

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
        from _balder.feature import Feature

        result = {}
        for cur_name in dir(self.related_cls):
            cur_val = getattr(self.related_cls, cur_name)
            if isinstance(cur_val, Feature):
                result[cur_name] = cur_val
        return result
