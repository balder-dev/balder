from __future__ import annotations
from typing import Type, Dict, Union, TYPE_CHECKING

import logging
from _balder.setup import Setup
from _balder.exceptions import IllegalVDeviceMappingError, MultiInheritanceError
from _balder.controllers.feature_controller import FeatureController
from _balder.controllers.device_controller import DeviceController
from _balder.controllers.normal_scenario_setup_controller import NormalScenarioSetupController

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__file__)


class SetupController(NormalScenarioSetupController):
    """
    This is the controller class for :class:`Setup` items.
    """

    # helper property to disable manual constructor creation
    __priv_instantiate_key = object()

    #: contains all existing setups and its corresponding controller object
    _items: Dict[Type[Setup], SetupController] = {}

    def __init__(self, related_cls, _priv_instantiate_key):

        # describes if the current controller is for setups or for scenarios (has to be set in child controller)
        self._related_type = Setup

        # this helps to make this constructor only possible inside the controller object
        if _priv_instantiate_key != SetupController.__priv_instantiate_key:
            raise RuntimeError('it is not allowed to instantiate a controller manually -> use the static method '
                               '`SetupController.get_for()` for it')

        if not isinstance(related_cls, type):
            raise TypeError('the attribute `related_cls` has to be a type (no object)')
        if not issubclass(related_cls, Setup):
            raise TypeError(f'the attribute `related_cls` has to be a sub-type of `{Setup.__name__}`')
        if related_cls == Setup:
            raise TypeError(f'the attribute `related_cls` is `{Setup.__name__}` - controllers for native type are '
                            f'forbidden')
        # contains a reference to the related class this controller instance belongs to
        self._related_cls = related_cls

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_for(related_cls: Type[Setup]) -> SetupController:
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """
        if SetupController._items.get(related_cls) is None:
            item = SetupController(related_cls, _priv_instantiate_key=SetupController.__priv_instantiate_key)
            SetupController._items[related_cls] = item

        return SetupController._items.get(related_cls)

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def related_cls(self) -> Type[Setup]:
        return self._related_cls

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_next_parent_class(self) -> Union[Type[Setup], None]:
        """
        This method returns the next parent class which is a subclass of the :class:`Setup` itself.

        :return: returns the next parent class or None if the next parent class is :class:`Setup`
                 itself
        """
        next_base_class = None
        for cur_base in self.related_cls.__bases__:
            if issubclass(cur_base, Setup):
                if next_base_class is not None:
                    raise MultiInheritanceError(
                        f"found more than one Setup parent classes for `{self.related_cls.__name__}` "
                        f"- multi inheritance is not allowed for Scenario/Setup classes")
                next_base_class = cur_base
        if next_base_class == Setup:
            return None
        return next_base_class

    def validate_feature_possibility(self):
        """
        This method validates that every feature connection (that already has a vDevice<->Device mapping on setup level)
        has a connection that is CONTAINED-IN the connection of the related setup devices.
        """
        all_devices = self.get_all_abs_inner_device_classes()
        for cur_device in all_devices:
            cur_device_instantiated_features = \
                DeviceController.get_for(cur_device).get_all_instantiated_feature_objects()
            for _, cur_feature in cur_device_instantiated_features.items():
                mapped_vdevice, mapped_device = cur_feature.active_vdevice_device_mapping
                if mapped_device is None:
                    # ignore this, because we have no vDevice mapping on setup level
                    continue

                cur_feature_controller = FeatureController.get_for(cur_feature.__class__)
                feature_class_based_for_vdevice = cur_feature_controller.get_abs_class_based_for_vdevice()
                if not feature_class_based_for_vdevice or mapped_vdevice not in feature_class_based_for_vdevice.keys():
                    # there exists no class based for vdevice information (at least for the current active vdevice)
                    continue

                # there exists a class based requirement for this vDevice
                class_based_cnn = feature_class_based_for_vdevice[mapped_vdevice]
                # search relevant connection
                cur_device_controller = DeviceController.get_for(cur_device)
                for _, cur_cnn_list in cur_device_controller.get_all_absolute_connections().items():
                    for cur_cnn in cur_cnn_list:
                        if not cur_cnn.has_connection_from_to(cur_device, end_device=mapped_device):
                            # this connection can be ignored, because it is no connection between the current device
                            # and the mapped device
                            continue
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
