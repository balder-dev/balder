from __future__ import annotations

from _balder.controllers.device_controller import DeviceController
from _balder.device import Device
from _balder.node_gateway import NodeGateway


def gateway(from_node: str, to_node: str, bidirectional: bool = True):
    """
    This decorator enables two nodes of a device to be connected to one another via a gateway. The gateway can
    implement an unidirectional or bidirectional connection.
    """
    if not isinstance(from_node, str) and not isinstance(to_node, str):
        raise ValueError("the value of `from_node` and `to_node` must be the name of the nodes (type `str`)")

    if isinstance(bidirectional, bool):
        raise ValueError("the value of `bidirectional` must be a `bool`")

    def decorator(cls):
        nonlocal from_node
        nonlocal to_node
        nonlocal bidirectional

        # it must be a class decorator
        if not issubclass(cls, Device):
            raise TypeError(
                f"The decorator `gateway` may only be used for `Device` objects. This is not possible for the applied "
                f"class `{cls.__name__}`.")
        decorated_cls_device_controller = DeviceController.get_for(cls)

        new_gateway = NodeGateway(cls, from_node, to_node, bidirectional)
        decorated_cls_device_controller.add_new_raw_gateway(new_gateway)
        return cls
    return decorator
