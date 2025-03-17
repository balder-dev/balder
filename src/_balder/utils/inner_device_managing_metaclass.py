from __future__ import annotations
import inspect
from _balder.device import Device


class InnerDeviceManagingMetaclass(type):
    """metaclass for all classes that holds :class:`Device` objects - sets the reference to the outer class for them"""
    def __new__(mcs, name, parents, dct):
        cls = super(InnerDeviceManagingMetaclass, mcs).__new__(mcs, name, parents, dct)
        for inner_item in dct.values():
            if inspect.isclass(inner_item) and issubclass(inner_item, Device):
                inner_item._outer_balder_class = cls

        return cls
