import logging
import balder
from balder.connections import UsbConnection, WifiConnection, IPv4Connection, EthernetConnection, \
    OpticalFiberConnection, TcpIPv4Connection, UdpIPv4Connection, WirelessLanConnection
from balder import Connection
from balder.exceptions import IllegalConnectionTypeError

logger = logging.getLogger(__name__)


def test_based_on_with_correct_single_resolved_members():
    """
    This test creates a simple connection tree that should be possible. This tree is already resolved and single!
    """
    subtree = IPv4Connection.based_on(EthernetConnection)
    logger.info("creation of a subtree with direct parent member is working as expected")
    assert subtree.is_resolved(), "the single resolved created subtree returns False while calling method " \
                                  "`is_resolved()`"
    assert subtree.is_single(), "the single resolved created subtree returns False while calling method `is_single()`"


def test_based_on_with_correct_non_resolved_members():
    """
    This test creates a simple connection tree that isn't resolved. Then it checks if this subtree matches the same
    subtree with all resolved members. In addition, the test secures that the subtree does not match with an inner
    subtree of itself.
    """
    subtree = IPv4Connection.based_on(OpticalFiberConnection)
    assert not subtree.is_resolved(), "the non-resolved created subtree returns True while calling method " \
                                      "`is_resolved()`"
    assert not subtree.is_single(), "the non-resolved created subtree returns True while calling method `is_single()`"
    assert subtree == IPv4Connection.based_on(EthernetConnection.based_on(OpticalFiberConnection)), \
        "comparing with complete created subtree returned true"
    assert subtree != IPv4Connection.based_on(EthernetConnection), \
        "comparing with a subtree of created subtree returned false"


def test_based_on_with_wrong_members():
    """
    This test checks if the `based_on` method throws the correct exception after the statement is not allowed.
    """
    try:
        UsbConnection.based_on(WifiConnection)
        assert False, "system thinks that USB is based on WIFI connection - and allows the creation of this tree"
    except IllegalConnectionTypeError as exc:
        logger.info(f"system raises error as expected (error message: `{str(exc)}`)")


def test_check_if_connection_container_is_resolved():
    """
    This test creates a simple connection tree that uses the raw `balder.Connection` as a container. The tree is
    already resolved but not single! The test secures that balder validates this correctly for all items of the
    container.
    """
    subtree = Connection.based_on(IPv4Connection.based_on(EthernetConnection) | UdpIPv4Connection)
    logger.info("creation of a subtree with a container class and two nested other connections is working as expected")
    assert subtree.is_resolved(), "the single resolved created subtree returns False while calling method " \
                                  "`is_resolved()`"
    assert not subtree.is_single(), "the single resolved created subtree returns True while calling method " \
                                    "`is_single()`"


def test_check_contained_in():
    """
    This test checks if the `contained_in()` method returns the correct values
    """
    subtree_outer = IPv4Connection.based_on(OpticalFiberConnection)
    assert Connection().contained_in(subtree_outer), 'the basic connection object `Connection` is not contained_in ' \
                                                     'the tree - that should return True'
    assert IPv4Connection().contained_in(subtree_outer), "IPv4Connection is not contained_in the tree - that should " \
                                                         "return True"
    assert EthernetConnection().contained_in(subtree_outer), "EthernetConnection is not contained_in the tree - that " \
                                                             "should return True"
    assert OpticalFiberConnection().contained_in(subtree_outer), "OpticalFiberConnection is not contained_in the tree" \
                                                                 " - that should return True"
    assert IPv4Connection.based_on(EthernetConnection).contained_in(subtree_outer), \
        "subtree with one element less is not contained_in the tree - that should return True"
    assert EthernetConnection.based_on(OpticalFiberConnection).contained_in(subtree_outer), \
        "subtree with one element less is not contained_in the tree - that should return True"
    assert subtree_outer.contained_in(subtree_outer), "contained_in with same object does not work (should return " \
                                                      "True)"
    assert IPv4Connection.based_on(OpticalFiberConnection).contained_in(subtree_outer), \
        "contained_in with same constructed object does not working (should return True)"
    assert not TcpIPv4Connection.based_on(OpticalFiberConnection).contained_in(subtree_outer), \
        "contained_in where bigger tree contained in smaller tree does not return False!"

    container_inner = Connection.based_on(UdpIPv4Connection | TcpIPv4Connection)

    assert container_inner.contained_in(UdpIPv4Connection()), \
        'the connection sub-tree with a container connection is not contained_in the outer tree ' \
        '`UdpIPv4Connection()` - that should return True'

    assert container_inner.contained_in(TcpIPv4Connection()), \
        'the connection sub-tree with a container connection is not contained_in the outer tree ' \
        '`TcpIPv4Connection()` - that should return True'

    double_parents_inner = IPv4Connection.based_on(EthernetConnection | WirelessLanConnection)

    assert double_parents_inner.contained_in(IPv4Connection.based_on(EthernetConnection)), \
        'the connection sub-tree with double parents is not contained_in the outer tree ' \
        '`EthernetConnection()` - that should return True'

    assert double_parents_inner.contained_in(IPv4Connection.based_on(WirelessLanConnection)), \
        'the connection sub-tree with double parents is not contained_in the outer tree ' \
        '`WirelessLanConnection()` - that should return True'

    and_items = Connection.based_on((EthernetConnection & WirelessLanConnection & UsbConnection))
    or_items = Connection.based_on(EthernetConnection | WirelessLanConnection | UsbConnection)

    assert not Connection.based_on((EthernetConnection & WirelessLanConnection)).contained_in(or_items)
    assert Connection.based_on((EthernetConnection & WirelessLanConnection)).contained_in(and_items)

    assert Connection.based_on(EthernetConnection).contained_in(and_items)
    assert EthernetConnection().contained_in(and_items)


def test_check_intersection_with():
    """
    This test checks if the `intersection_with()` method returns the correct values
    """
    # nonsense (should be always empty)
    assert EthernetConnection().intersection_with(IPv4Connection()) is None
    assert Connection.based_on(EthernetConnection).intersection_with(IPv4Connection()) is None
    assert EthernetConnection().intersection_with(Connection.based_on(IPv4Connection)) is None

    # empty connection container
    assert Connection().intersection_with(EthernetConnection) == EthernetConnection()
    assert EthernetConnection().intersection_with(Connection()) == EthernetConnection()

    double_parents = IPv4Connection.based_on(EthernetConnection | WirelessLanConnection)

    # simple first based on element (without container)
    assert double_parents.intersection_with(EthernetConnection()) == EthernetConnection()
    assert EthernetConnection().intersection_with(double_parents) == EthernetConnection()

    # simple second based on element (without container)
    assert double_parents.intersection_with(WirelessLanConnection()) == WirelessLanConnection()
    assert WirelessLanConnection().intersection_with(double_parents) == WirelessLanConnection()

    # simple child element (without container)
    assert double_parents.intersection_with(IPv4Connection()) == IPv4Connection()
    assert IPv4Connection().intersection_with(double_parents) == IPv4Connection()

    # simple first based on element (with container)
    assert Connection.based_on(double_parents).intersection_with(EthernetConnection()) == EthernetConnection()
    assert double_parents.intersection_with(Connection.based_on(EthernetConnection)) == EthernetConnection()
    assert Connection.based_on(EthernetConnection).intersection_with(double_parents) == EthernetConnection()
    assert EthernetConnection().intersection_with(Connection.based_on(double_parents)) == EthernetConnection()

    # simple second based on element (with container)
    assert Connection.based_on(double_parents).intersection_with(WirelessLanConnection()) == WirelessLanConnection()
    assert double_parents.intersection_with(Connection.based_on(WirelessLanConnection)) == WirelessLanConnection()
    assert Connection.based_on(WirelessLanConnection).intersection_with(double_parents) == WirelessLanConnection()
    assert WirelessLanConnection().intersection_with(Connection.based_on(double_parents)) == WirelessLanConnection()

    # simple child element (with container)
    assert Connection.based_on(double_parents).intersection_with(IPv4Connection()) == IPv4Connection()
    assert double_parents.intersection_with(Connection.based_on(IPv4Connection)) == IPv4Connection()
    assert Connection.based_on(IPv4Connection).intersection_with(double_parents) == IPv4Connection()
    assert IPv4Connection().intersection_with(Connection.based_on(double_parents)) == IPv4Connection()

    first_branch = IPv4Connection.based_on(EthernetConnection)
    second_branch = IPv4Connection.based_on(WirelessLanConnection)

    # chain first based on element (without container)
    assert double_parents.intersection_with(first_branch) == first_branch
    assert first_branch.intersection_with(double_parents) == first_branch

    # chain second based on element (without container)
    assert double_parents.intersection_with(second_branch) == second_branch
    assert second_branch.intersection_with(double_parents) == second_branch

    # chain first based on element (with container)
    assert Connection.based_on(double_parents).intersection_with(first_branch) == first_branch
    assert double_parents.intersection_with(Connection.based_on(first_branch)) == first_branch
    assert Connection.based_on(first_branch).intersection_with(double_parents) == first_branch
    assert first_branch.intersection_with(Connection.based_on(double_parents)) == first_branch

    # chain second based on element (with container)
    assert Connection.based_on(double_parents).intersection_with(second_branch) == second_branch
    assert double_parents.intersection_with(Connection.based_on(second_branch)) == second_branch
    assert Connection.based_on(second_branch).intersection_with(double_parents) == second_branch
    assert second_branch.intersection_with(Connection.based_on(double_parents)) == second_branch

    # multiple container elements with single one
    assert Connection.based_on(EthernetConnection | WirelessLanConnection).intersection_with(EthernetConnection) == \
           EthernetConnection()

    # basic AND connection tests
    assert Connection.based_on(EthernetConnection & WirelessLanConnection).intersection_with(
        Connection.based_on(EthernetConnection & WirelessLanConnection)) == Connection.based_on(
        EthernetConnection() & WirelessLanConnection())
    assert Connection.based_on(EthernetConnection | EthernetConnection & WirelessLanConnection).intersection_with(
        Connection.based_on(EthernetConnection & WirelessLanConnection)) == Connection.based_on(
        EthernetConnection() & WirelessLanConnection())
    assert Connection.based_on(EthernetConnection | EthernetConnection & WirelessLanConnection).intersection_with(
        EthernetConnection) == EthernetConnection()
