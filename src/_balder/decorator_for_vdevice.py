from __future__ import annotations
from typing import Union, Type

import inspect
from _balder.cnnrelations import AndConnectionRelation, OrConnectionRelation
from _balder.collector import Collector
from _balder.feature import Feature
from _balder.vdevice import VDevice
from _balder.connection import Connection
from _balder.controllers import FeatureController
from _balder.exceptions import DuplicateForVDeviceError, UnknownVDeviceException


def for_vdevice(
        vdevice: Union[str, Type[VDevice]],
        with_connections: Union[
            Type[Connection], Connection, AndConnectionRelation, OrConnectionRelation
        ] = Connection(),
):
    """
    With the `@for_vdevice` you can limit the decorated object for a special allowed connection tree for every existing
    vDevice. This decorator can be used to decorate whole :class:`Feature` classes just like single methods of a
    :class:`Feature` class.

    Decorated Feature classes: This controls the allowed sub-connection tree between the mapped device of the given
                               vDevice and the device class that uses the decorated feature. If the defined sub-tree
                               does not match the sub-tree that connects the both devices with each other on the setup
                               level, the feature can not be applied.

    Decorated Feature method: Similar to the class based decoration, you can specify if a method is executable with
                              the given sub-tree. Especially, at this point you are able to define your own method
                              variations. Balder will select the chosen one depending on the matching connection
                              sub-tree.

    You can find more about this in the documentation chapter :ref:`VDevices and method-variations`.

    :param vdevice: the vDevice this decorator should describe

    :param with_connections: the assigned connection trees for this class/method (default: a universal connection)
    """
    if isinstance(with_connections, Connection):
        # do nothing
        pass
    elif isinstance(with_connections, (AndConnectionRelation, OrConnectionRelation)):
        # use container connection
        with_connections = Connection.based_on(with_connections)
    elif isinstance(with_connections, type) and issubclass(with_connections, Connection):
        # instantiate it
        with_connections = with_connections()
    else:
        raise TypeError(f"the given element ``with_connection`` needs to be from type `AndConnectionRelation`, "
                        f"`OrConnectionRelation` or `Connection` - `{type(with_connections)}` is not allowed")

    # note: if `args` is an empty list - no special sub-connection-tree bindings

    if not (isinstance(vdevice, str) or (isinstance(vdevice, type) and issubclass(vdevice, VDevice))):
        raise ValueError('the given element for `vdevice` has to be a `str` or has to be a subclass of'
                         '`VDevice`')

    class ForVDeviceDecorator:
        """decorator class for `@for_vdevice` decorator"""

        def __init__(self, func):
            nonlocal vdevice
            nonlocal with_connections

            self.func = func

            # we detect a decorated non-class object -> save it and check it later in collector
            Collector.register_possible_method_variation(func, vdevice, with_connections)

        def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
            nonlocal vdevice

            func = args[0]

            if inspect.isclass(func):
                # it must be a class decorator
                if not issubclass(func, Feature):
                    raise TypeError(f"The decorator `@for_vdevice` may only be used for `Feature` objects. This is "
                                    f"not possible for the applied class `{func.__name__}`.")

                fn_feature_controller = FeatureController.get_for(func)

                if isinstance(vdevice, str):
                    # vDevice is a string, so we have to convert it to the correct class
                    relevant_vdevices = [cur_vdevice for cur_vdevice
                                         in fn_feature_controller.get_abs_inner_vdevice_classes()
                                         if cur_vdevice.__name__ == vdevice]

                    if len(relevant_vdevices) == 0:
                        raise ValueError(
                            f"can not find a matching inner VDevice class for the given vDevice string `{vdevice}` in "
                            f"the feature class `{func.__name__}`")

                    if len(relevant_vdevices) > 1:
                        raise RuntimeError("found more than one possible vDevices - something unexpected happened")

                    vdevice = relevant_vdevices[0]
                cls_for_vdevice = fn_feature_controller.get_class_based_for_vdevice()
                if vdevice in cls_for_vdevice.keys():
                    raise DuplicateForVDeviceError(
                        f'there already exists a decorator for the vDevice `{vdevice}` in the Feature class '
                        f'`{func.__name__}`')
                if vdevice not in fn_feature_controller.get_abs_inner_vdevice_classes():
                    raise UnknownVDeviceException(
                        f"the given vDevice `{vdevice}` is no usable vDevice in Feature class `{func.__name__}`")

                cls_for_vdevice[vdevice] = with_connections
                fn_feature_controller.set_class_based_for_vdevice(cls_for_vdevice)
                # directly return the class -> we do not want to manipulate it
                return func

            # otherwise, work will be done in `__init__`
            # return this decorator object to work with
            return super().__new__(ForVDeviceDecorator)

    return ForVDeviceDecorator
