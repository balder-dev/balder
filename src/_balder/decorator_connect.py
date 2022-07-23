from __future__ import annotations
from typing import Type, Union

from _balder.device import Device

import re
from _balder.connection import Connection
from _balder.controllers import DeviceController


def connect(with_device: Union[Type[Device], str], over_connection: Union[Type[Connection], Connection],
            self_node_name: str = None, dest_node_name: str = None):
    """
    This decorator connects two devices with each other. It can be used for scenarios as well as setup devices.

    :param with_device: that's the :class:`Device` that should be connected to the decorated device

    :param over_connection: that's the connection tree that should connect the devices with each other

    :param self_node_name: the node name of this device (if this param is not given, balder automatically generates a
                           new node name in format `n{unique device counter}`)

    :param dest_node_name: the node name of the destination device, given with `with_device` (if this param is not
                           given, balder automatically generates a new node name in format `n{unique device counter}`)
    """
    ALLOWED_REGEX_AUTO_NODE_NAMES = r"n[0-9]+"

    if not isinstance(with_device, str) and not issubclass(with_device, Device):
        raise ValueError("the value of `with_device` must be a `Device` (or a subclass thereof) or the device name "
                         "as a string")
    if isinstance(over_connection, tuple):
        # doesn't make sense, because we can describe what's needed in one scenario with several `@connect` decorations
        # anyway. We are describing a setup, therefore an AND link makes no sense here either
        raise TypeError("an AND link (signaled via the tuple) of the connection is not possible here - for further "
                        "separate connections use the `@connect` decorator again")
    if isinstance(over_connection, type):
        if not issubclass(over_connection, Connection):
            raise TypeError("the type of `over_connection` must be a `Connection` (or a subclass of it)")
    elif not isinstance(over_connection, Connection):
        raise TypeError("the type of `over_connection` must be a `Connection` (or a subclass of it)")

    if self_node_name is not None:
        if not isinstance(self_node_name, str):
            raise TypeError("the type of `node_name` must be a `str`")
        if re.match(ALLOWED_REGEX_AUTO_NODE_NAMES, self_node_name):
            raise ValueError(
                f"the given `self_node_name` matches the regular expression `{ALLOWED_REGEX_AUTO_NODE_NAMES}` that is "
                f"reserved for internal node naming and should not be used by you")
    if dest_node_name is not None:
        if not isinstance(dest_node_name, str):
            raise TypeError("the type of `node_name` must be a `str`")
        if re.match(ALLOWED_REGEX_AUTO_NODE_NAMES, dest_node_name):
            raise ValueError(
                f"the given `dest_node_name` matches the regular expression `{ALLOWED_REGEX_AUTO_NODE_NAMES}` that is "
                f"reserved for internal node naming and should not be used by you")

    class MyDecorator:
        """
        This decorator will add the connection to the device that is decorated. If the `with_device` is no other device
        class (given as string) this decorator can not handle the node allocation and the device resolving (because not
        all devices are resolved yet). In this case the function adds the device-string in the :class:`Connection`
        object and if the `dest_node_name` is None, it will also set this value to None. This secure that the
        collector will create a unique auto node for it.
        """
        def __new__(cls, *args, **kwargs):

            decorated_cls = args[0]
            nonlocal with_device
            nonlocal over_connection
            nonlocal self_node_name
            nonlocal dest_node_name

            this_outer_class_name, _ = decorated_cls.__qualname__.split('.')
            if not isinstance(with_device, str):
                other_outer_class_name, _ = with_device.__qualname__.split('.')
                if this_outer_class_name != other_outer_class_name:
                    raise ValueError(f"the given device is not mentioned in this setup/scenario - please create a new "
                                     f"direct inner device class, it can be inherited from `{with_device.__qualname__}`")
            decorated_cls_device_controller = DeviceController.get_for(decorated_cls)

            # if required give auto name to nodes
            if self_node_name is None:
                self_node_name = decorated_cls_device_controller.get_new_empty_auto_node()
            if dest_node_name is None and not isinstance(with_device, str):
                with_device_controller = DeviceController.get_for(with_device)
                dest_node_name = with_device_controller.get_new_empty_auto_node()

            cur_cnn_instance = None
            if isinstance(over_connection, Connection):
                # already instantiated because it comes back from a `based_on` - clone it to secure that it was not used
                #  in another `@connect()` decorator (and also remove possible metadata from the new clone)
                cur_cnn_instance = over_connection.clone()
                cur_cnn_instance.set_metadata_for_all_subitems(None)
            elif issubclass(over_connection, Connection):
                # not instantiated -> instantiate it
                cur_cnn_instance = over_connection()
            cur_cnn_instance.set_devices(from_device=decorated_cls, to_device=with_device)
            cur_cnn_instance.update_node_names(from_device_node_name=self_node_name, to_device_node_name=dest_node_name)

            decorated_cls_device_controller.add_new_raw_connection(cur_cnn_instance)
            return decorated_cls
    return MyDecorator
