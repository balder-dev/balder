from _balder.routing_path import RoutingPath
import balder


class Device1(balder.Device):
    pass


class Device2(balder.Device):
    pass


class Device3(balder.Device):
    pass


def test_route_loop_detection_with_2():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` detects a simple 2 device loop.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn20_10 = balder.Connection(
        from_device=Device2, from_device_node_name='0', to_device=Device1, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn20_10)

    assert path.has_loop() is True, "does not detect a loop, while using two similar unidirectional connections"


def test_route_loop_detection_with_2_no_loop():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` does not detect a loop if no devices overlap.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn20_30 = balder.Connection(
        from_device=Device2, from_device_node_name='0', to_device=Device3, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn20_30)

    assert path.has_loop() is False, "does detect a loop, while no loop should be detected"


def test_route_loop_detection_with_2_with_inverse_cnn():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` detects a simple 2 device loop, while one connection
    is inverse.
    """

    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn10_20_second = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn10_20_second)

    assert path.has_loop() is True, "does not detect a loop, while using two similar unidirectional connections"


def test_route_loop_detection_with_3():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` detects a simple 3 device loop.
    """
    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn20_30 = balder.Connection(
        from_device=Device2, from_device_node_name='0', to_device=Device3, to_device_node_name='0')
    cnn30_10 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device1, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn20_30)
    path.append_element(cnn30_10)

    assert path.has_loop() is True, "does not detect a loop, while using three similar bidirectional connections"


def test_route_loop_detection_with_3_with_inverse_cnn():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` detects a simple 3 device loop, while the second
    connection is inverse.
    """
    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn30_20 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn30_10 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device1, to_device_node_name='0')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn30_20)
    path.append_element(cnn30_10)

    assert path.has_loop() is True, "does not detect a loop, while using three similar bidirectional connections"


def test_route_loop_detection_with_3_no_loop_because_of_different_node():
    """
    This test checks that the method :meth:`RoutingPath.has_loop` does not find a loop, if one connections goes to the
    same device but to a different node.
    """
    cnn10_20 = balder.Connection(
        from_device=Device1, from_device_node_name='0', to_device=Device2, to_device_node_name='0')
    cnn20_30 = balder.Connection(
        from_device=Device2, from_device_node_name='0', to_device=Device3, to_device_node_name='0')
    cnn30_11 = balder.Connection(
        from_device=Device3, from_device_node_name='0', to_device=Device1, to_device_node_name='1')

    path = RoutingPath(cnn10_20, start_device=Device1, start_node_name='0')
    path.append_element(cnn20_30)
    path.append_element(cnn30_11)

    assert path.has_loop() is False, "does detect a loop, while one connection goes to a previously device but "
