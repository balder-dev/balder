from __future__ import annotations
from typing import Dict, Tuple, Type

import inspect
from _balder.collector import Collector
from _balder.device import Device
from _balder.parametrization import FeatureAccessSelector, Parameter, Value


def parametrize_by_feature(
        field_name: str,
        feature_accessor: Tuple[Type[Device], str, str],
        parameter: Dict[str, FeatureAccessSelector | Parameter | Value] = None
):
    """
    Allows to parametrize a test function. This decorator will be used to dynamically parametrize a test function, by
    the value a setup feature returns before entering the test.

    :param field_name: the field name of the test function
    :param feature_accessor: a tuple that provides information for accessing the feature
    :param parameter: the parameter to parametrize the feature method (if necessary)
    """
    if not isinstance(field_name, str):
        raise ValueError('the given field name must be a string')
    if parameter is None:
        parameter = {}

    feature_accessor = FeatureAccessSelector(*feature_accessor, parameters=parameter)

    def decorator(func):
        if not inspect.isfunction(func):
            raise TypeError('the decorated object needs to be a test method')

        Collector.register_possible_parametrization(func, field_name, feature_accessor)
        return func
    return decorator
