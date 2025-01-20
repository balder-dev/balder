import balder
from balder.connections import DnsConnection


def test_connection_from_to():
    """
    This test checks if the method :meth:`Connection.has_connection_from_to` works correctly.
    """
    class Device1(balder.Device):
        pass

    class Device2(balder.Device):
        pass

    conn = DnsConnection(from_device=Device1, from_device_node_name='ntest1', to_device=Device2,
                         to_device_node_name='ntest2')

    assert conn.has_connection_from_to(Device1), "method does not return true"
    assert conn.has_connection_from_to(Device1, end_device=Device2), "method does not return true"
    assert conn.has_connection_from_to(Device2), "method does not return true, although this is a " \
                                                 "bidirectional connection"
    assert conn.has_connection_from_to(Device2, end_device=Device1), "method does not return true, although this is a " \
                                                                     "bidirectional connection"
