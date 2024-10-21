from __future__ import annotations
from typing import Type, Dict, Any, TypeVar, List
import dataclasses

from _balder.device import Device

ValueTypeT = TypeVar("ValueTypeT")


@dataclasses.dataclass
class FeatureAccessSelector:
    """helper object for dynamic parametrizing by feature method/property"""
    device: Type[Device]
    device_property_name: str
    feature_property_name: str
    parameters: Dict[str, FeatureAccessSelector | Value] = dataclasses.field(default_factory=dict)

    def get_value(self, available_parameters: Dict[str, Any]) -> List[Any]:
        """accesses the configured method/property"""
        resolved_parameters = {}
        for cur_key, cur_value in self.parameters.items():
            if isinstance(cur_value, FeatureAccessSelector):
                resolved_parameters[cur_key] = cur_value.get_value(available_parameters)
            elif isinstance(cur_value, Parameter):
                resolved_parameters[cur_key] = available_parameters[cur_value.name]
            elif isinstance(cur_value, Value):
                resolved_parameters[cur_key] = cur_value.value
            else:
                raise TypeError(f'go unexpected parameter type {type(cur_value)} in FeatureAccessSelector')

        feature = getattr(self.device, self.device_property_name)

        if isinstance(getattr(feature.__class__, self.feature_property_name), property):
            return getattr(feature, self.feature_property_name)

        return getattr(feature, self.feature_property_name)(**resolved_parameters)

    def get_parameters(
            self,
            of_type: Type[FeatureAccessSelector | Parameter | Value] | None = None
    ) -> Dict[str, FeatureAccessSelector | Parameter | Value]:
        """
        Returns the parameters of this access selector

        :param of_type: allows to filter the parameters by the value's type
        """
        result = {}
        for cur_attr, cur_value in self.parameters.items():
            if of_type is None or isinstance(cur_value, of_type):
                result[cur_attr] = cur_value
        return result


class Parameter:
    """allows to parametrize a parametrization by another parametrization value"""

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """returns the name of the parameter"""
        return self._name


class Value:
    """allows to parametrize a parametrization by a fix value"""

    def __init__(self, value: ValueTypeT) -> None:
        self._value = value

    @property
    def value(self) -> ValueTypeT:
        """returns the value of the parametrization"""
        return self._value
