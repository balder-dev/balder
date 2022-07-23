from __future__ import annotations
from typing import List, Union, Type, Tuple

import inspect
from _balder.collector import Collector
from _balder.feature import Feature
from _balder.device import Device
from _balder.vdevice import VDevice
from _balder.connection import Connection
from _balder.controllers import FeatureController
from _balder.exceptions import DuplicateForVDeviceError, UnknownVDeviceException


def for_vdevice(
        vdevice: Union[str, Device],
        with_connections: Union[
            Type[Connection], Connection, Tuple[Union[Type[Connection], Connection]],
            List[Union[Type[Connection], Connection, Tuple[Union[Type[Connection], Connection]]]]] = Connection(),
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
    idx = 0
    if not isinstance(with_connections, list):
        with_connections = [with_connections]
    for cur_conn in with_connections:
        if isinstance(cur_conn, type):
            if not issubclass(cur_conn, Connection):
                raise ValueError(f"the given element type for the element on position `{idx}` has to be a subclass of "
                                 f"`{Connection.__name__}` or a element of it")
        elif isinstance(cur_conn, tuple):
            tuple_idx = 0
            for cur_tuple_elem in cur_conn:
                if not isinstance(cur_tuple_elem, Connection) and not issubclass(cur_tuple_elem, Connection):
                    raise ValueError(f"the given tuple element `{tuple_idx}` that is given on position `{idx}` "
                                     f"has to be a subclass of `{Connection.__name__}`")
                tuple_idx += 1
        elif not isinstance(cur_conn, Connection):
            raise ValueError(f"the given type on position `{idx}` has to be a subclass of `{Connection.__name__}` or "
                             f"a element of it")

        idx += 1
    # note: if `args` is an empty list - no special sub-connection-tree bindings

    if not isinstance(vdevice, str) and not isinstance(vdevice, VDevice):
        raise ValueError('the given element for `vdevice` has to be a `str` or has to be a subclass of'
                         '`VDevice`')

    class ForConnectionDecorator:

        def __init__(self, fn):
            nonlocal vdevice
            nonlocal with_connections

            self.fn = fn

            # we detect a decorated non-class object -> save it and check it later in collector
            if fn not in Collector._possible_method_variations.keys():
                Collector._possible_method_variations[fn] = []
            Collector._possible_method_variations[fn].append((vdevice, with_connections))

        def __new__(cls, *args, **kwargs):
            nonlocal vdevice

            fn = args[0]

            if inspect.isclass(fn):
                # it must be a class decorator
                if not issubclass(fn, Feature):
                    raise TypeError(f"The decorator `@for_vdevice` may only be used for `Feature` objects. This is "
                                    f"not possible for the applied class `{fn.__name__}`.")

                fn_feature_controller = FeatureController.get_for(fn)

                if isinstance(vdevice, str):
                    # vDevice is a string, so we have to convert it to the correct class
                    relevant_vdevices = [cur_vdevice for cur_vdevice
                                         in fn_feature_controller.get_abs_inner_vdevice_classes()
                                         if cur_vdevice.__name__ == vdevice]
                    if len(relevant_vdevices) == 0:
                        raise ValueError(
                            f"can not find a matching inner VDevice class for the given vDevice string `{vdevice}` in "
                            f"the feature class `{fn.__name__}`")
                    elif len(relevant_vdevices) > 1:
                        raise RuntimeError("found more than one possible vDevices - something unexpected happened")
                    vdevice = relevant_vdevices[0]
                cls_for_vdevice = fn_feature_controller.get_class_based_for_vdevice()
                cls_for_vdevice = {} if cls_for_vdevice is None else cls_for_vdevice
                if vdevice in cls_for_vdevice.keys():
                    raise DuplicateForVDeviceError(
                        f'there already exists a decorator for the vDevice `{vdevice}` in the Feature class '
                        f'`{fn.__name__}`')
                if vdevice not in fn_feature_controller.get_abs_inner_vdevice_classes():
                    raise UnknownVDeviceException(
                        f"the given vDevice `{vdevice}` is no usable vDevice in Feature class `{fn.__name__}`")

                cls_for_vdevice[vdevice] = [cur_cnn for cur_cnn in with_connections]
                fn_feature_controller.set_class_based_for_vdevice(cls_for_vdevice)
                # directly return the class -> we do not want to manipulate it
                return fn
            else:
                # work will done in `__init__`

                # return this decorator object to work with
                return super().__new__(ForConnectionDecorator)

    return ForConnectionDecorator
