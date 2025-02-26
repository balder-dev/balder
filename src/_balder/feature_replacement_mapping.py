from typing import Union, Type
import dataclasses
from .device import Device
from .feature import Feature
from .controllers import DeviceController


class FeatureReplacementMapping:
    """
    helper object that stores mappings between scenario and setup features - is used in :class:`VariationExecutor`
    """

    @dataclasses.dataclass
    class FeatureMapping:
        """
        stores a single mapping
        """
        #: the feature attribute name in scenario device
        attr_name: str
        #: the scenario feature instance or None if the current variation does not use this setup feature in scenario
        scenario_feature: Union[Feature, None]
        #: the setup feature that is used for the scenario feature
        setup_feature: Feature

    def __init__(self):
        self._mappings: list[FeatureReplacementMapping.FeatureMapping] = []

    @property
    def mappings(self) -> list[FeatureMapping]:
        """
        returns all existing mappings
        """
        return list(self._mappings)

    @property
    def attr_names(self) -> list[str]:
        """
        returns all used attribute names
        """
        return [mapping.attr_name for mapping in self._mappings]

    @property
    def all_scenario_features(self) -> list[Feature]:
        """
        returns all scenario features
        """
        return [mapping.scenario_feature for mapping in self._mappings]

    @property
    def all_setup_features(self) -> list[Feature]:
        """
        returns all setup features
        """
        return [mapping.setup_feature for mapping in self._mappings]

    def add(self, attr_name: str, scenario_feature: Union[Feature, None], setup_feature: Feature):
        """
        adds a new mapping

        :param attr_name: the feature attribute name in scenario device
        :param scenario_feature: the scenario feature instance or None if the current variation does not use this setup
                                 feature in scenario
        :param setup_feature: the setup feature that is used for the scenario feature
        """
        if attr_name in self.attr_names:
            raise KeyError(f'entry for property name `{attr_name}` already exist - can not define it multiple times')
        self._mappings.append(FeatureReplacementMapping.FeatureMapping(attr_name, scenario_feature, setup_feature))

    def get_features_for_attr_name(self, attr_name: str) -> tuple[Feature, Feature]:
        """
        returns the scenario and its mapped setup feature for a specific attribute name used in the scenario device
        """
        for mapping in self._mappings:
            if mapping.attr_name == attr_name:
                return mapping.scenario_feature, mapping.setup_feature
        raise KeyError(f'entry for property name `{attr_name}` does not exist')

    def get_replaced_scenario_feature_for(self, setup_feature: Feature) -> Union[Feature, None]:
        """
        returns the mapped scenario feature for a given setup feature
        """
        for mapping in self._mappings:
            if mapping.setup_feature == setup_feature:
                return mapping.scenario_feature
        raise KeyError(f'cannot find setup feature for {setup_feature}')

    def add_remaining_setup_features_as_autonomous(self, cur_setup_device: Type[Device]):
        """
        Adds all features that were not added as autonomous features.
        """
        cur_setup_features = DeviceController.get_for(cur_setup_device).get_all_instantiated_feature_objects()

        # also add all setup features that are not assigned as autonomous features
        for cur_setup_feature in cur_setup_features.values():
            if cur_setup_feature not in self.all_setup_features:
                # determine free name
                idx = 0
                autonomous_name = None
                while (autonomous_name is None
                       or autonomous_name in self.attr_names):
                    autonomous_name = f"_autonomous_feat_{idx}"
                    idx += 1
                self.add(
                    attr_name=autonomous_name,
                    scenario_feature=None,
                    setup_feature=cur_setup_feature
                )
