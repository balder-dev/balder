from _balder.routing_path import RoutingPath
from balder.exceptions import RoutingBrokenChainError
import balder


class Device1(balder.Device):
    pass


class Device2(balder.Device):
    pass


class Device3(balder.Device):
    pass


class Device4(balder.Device):
    pass


def test_simple_valid_route_over_3_devs():
    """
    This test validates the :class:`RoutingPath` for a valid connection from `Device1` -> `Device2` -> `Device3`.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn20_30 = balder.Connection(
        from_device=Device2, from_device_node_name='0', to_device=Device3, to_device_node_name='0')
    cnn10_30 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device3, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn20_30)

    assert path.get_virtual_connection() == cnn10_30


def test_simple_valid_route_over_3_devs_with_inverse_def():
    """
    This test validates the :class:`RoutingPath` for a valid connection from `Device1` -> `Device2` -> `Device3`.
    The second connection is defined inverse, which means, that the from-device is `Device3` instead of `Device1`. As
    all connection are bidirectional, this should work without any problems.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn30_20 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn10_30 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device3, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn30_20)

    assert path.get_virtual_connection() == cnn10_30


def test_invalid_route_wrong_node():
    """
    This test checks that the method :meth:`RoutingPath.append_element` throws a :class:`RoutingBrokenChainError`
    if the device-node-name is not the same as the end-node-name of the last element before the new connection is added.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn21_30 = balder.Connection(
        from_device=Device2, from_device_node_name='1', to_device=Device3, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    try:
        path.append_element(cnn21_30)
    except RoutingBrokenChainError as exc:
        assert exc.args[0] == 'can not append connection, because neither the from-device/node ' \
                              '(device: `Device2` | node: `1`) nor the to-device/node ' \
                              '(device: `Device3` | node: `0`) of the connection match with the latest ' \
                              'end-device/node (device: `Device2` | node: `0`) of this route'


def test_invalid_route_wrong_node_with_inverse_def():
    """
    This test checks that the method :meth:`RoutingPath.append_element` throws a :class:`RoutingBrokenChainError`
    if the device-node-name is not the same as the end-node-name of the last element before the new connection is added.

    The second connection is defined inverse, which means, that the from-device is `Device3` instead of `Device1`. As
    all connection are bidirectional, this should also throw the wrong node error.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn30_21 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device2, to_device_node_name='1')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    try:
        path.append_element(cnn30_21)
    except RoutingBrokenChainError as exc:
        assert exc.args[0] == 'can not append connection, because neither the from-device/node ' \
                              '(device: `Device3` | node: `0`) nor the to-device/node ' \
                              '(device: `Device2` | node: `1`) of the connection match with the latest ' \
                              'end-device/node (device: `Device2` | node: `0`) of this route'


def test_invalid_route_no_dev():
    """
    This test checks, that the method :meth:`RoutingPath.append_element` throws a :class:`RoutingBrokenChainError` in
    case a connection will be added that does not have the current end-device.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn30_40 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device4, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    try:
        path.append_element(cnn30_40)
    except RoutingBrokenChainError as exc:
        assert exc.args[0] == 'can not append connection, because neither the from-device/node ' \
                              '(device: `Device3` | node: `0`) nor the to-device/node ' \
                              '(device: `Device4` | node: `0`) of the connection match with the latest ' \
                              'end-device/node (device: `Device2` | node: `0`) of this route'


def test_invalid_route_diff_dev_and_diff_node():
    """
    This test checks, that the method :meth:`RoutingPath.append_element` throws a :class:`RoutingBrokenChainError` in
    case a connection will be added that does not have the current end-device and current end-device-node-name.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn31_41 = balder.Connection(
        from_device=Device3, from_device_node_name='1', to_device=Device4, to_device_node_name='1')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    try:
        path.append_element(cnn31_41)
    except RoutingBrokenChainError as exc:
        assert exc.args[0] == 'can not append connection, because neither the from-device/node ' \
                              '(device: `Device3` | node: `1`) nor the to-device/node ' \
                              '(device: `Device4` | node: `1`) of the connection match with the latest ' \
                              'end-device/node (device: `Device2` | node: `0`) of this route'
