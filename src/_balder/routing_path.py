from __future__ import annotations
from typing import List, Union, Dict, Type, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.device import Device

import copy
from _balder.connection import Connection
from _balder.node_gateway import NodeGateway
from _balder.controllers import DeviceController
from _balder.exceptions import RoutingBrokenChainError


class RoutingPath:
    """
    This object describes a possible routing path between two devices (which may be possible via several individual
    connections). If there are several possible paths between two devices, there are correspondingly many of these
    RoutingPath objects.
    """

    def __init__(self, *routing_elems: Union[Connection, NodeGateway], start_device: Type[Device],
                 start_node_name: str):
        """
        :param routing_elems: all elements that are parts of this route

        :param start_device: the device this route starts with (if the first element is a gateway this is optional)

        :param start_node_name: the node this route starts from (always required!)
        """

        self._routing_elems = []

        self._start_device = start_device
        self._start_node_name = start_node_name

        if not isinstance(routing_elems[0], Connection):
            raise TypeError("the first element is no `Connection` object - every route has to start and end with a"
                            "`Connection` object")
        if not isinstance(routing_elems[-1], Connection):
            raise TypeError("the last element is no `Connection` object - every route has to start and end with a"
                            "`Connection` object")

        first_elem = routing_elems[0]
        if isinstance(first_elem, Connection):
            if first_elem.from_device != self._start_device and first_elem.to_device != self._start_device:
                raise ValueError(f"the given `start_device={self._start_device.__name__}` does not match with one of "
                                 f"the available devices of the first routing element")
            if first_elem.from_node_name != self._start_node_name and \
                    first_elem.to_node_name != self._start_node_name:
                raise ValueError(f"the given `start_node_name={self._start_node_name}` does not match with one of the "
                                 f"available node names of the first routing element")
        else:
            raise TypeError(f"the first given element is not an instance of `{Connection.__name__}` or "
                            f"`{NodeGateway.__name__}` (is `{type(first_elem)}`)")

        for cur_elem in routing_elems:
            self.append_element(cur_elem)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def route_through(
            scenario_connection: Connection, device_mapping: Dict[Type[Device], Type[Device]],
            alternative_setup_device_cnns: Union[List[Connection], None] = None) \
            -> List[RoutingPath]:
        """
        This static method tries to route the given ``scenario_connection`` with the device_mapping. It returns a list
        of all matched routings between the mapped devices, where the routing is valid to support the requested
        `scenario_connection`.

        :param scenario_connection: the scenario-device connection object

        :param device_mapping: the used device mapping for the given `scenario_connection`

        :param alternative_setup_device_cnns: the alternative used connections between all relevant setup devices (if
                                              this is none, the router uses the setup-device connections from method
                                              `get_all_absolute_connections()`, otherwise it uses this dictionary here)
        """
        setup_devices_cnns = alternative_setup_device_cnns
        if alternative_setup_device_cnns is None:
            setup_devices_cnns = []
            for cur_setup_device in device_mapping.values():
                cur_setup_device_abs_cnns = \
                    DeviceController.get_for(cur_setup_device).get_all_absolute_connections()
                for _, cur_cnn_list in cur_setup_device_abs_cnns.items():
                    for cur_cnn in cur_cnn_list:
                        if cur_cnn not in setup_devices_cnns:
                            setup_devices_cnns.append(cur_cnn)

        from_scenario_device = scenario_connection.from_device
        to_scenario_device = scenario_connection.to_device
        from_setup_device = device_mapping[from_scenario_device]
        to_setup_device = device_mapping[to_scenario_device]

        # contains a list with all routes that start and end correctly
        all_completed_routes = []
        # contains a list with all possible routes
        all_possible_routes = []

        # add all connection objects that are mentioned in `from_setup_device`
        for cur_from_setup_node_conn in setup_devices_cnns:
            # only if there is a connection outgoing from `from_setup_device`
            if cur_from_setup_node_conn.has_connection_from_to(start_device=from_setup_device):
                cur_from_setup_node = cur_from_setup_node_conn.from_node_name \
                    if cur_from_setup_node_conn.from_device == from_setup_device \
                    else cur_from_setup_node_conn.to_node_name
                new_route = RoutingPath(cur_from_setup_node_conn, start_device=from_setup_device,
                                        start_node_name=cur_from_setup_node)
                all_possible_routes.append(new_route)
        # now go through every possibility and add them - filter all Routes that ``has_loop() == True`` or
        # are completed
        while len(all_possible_routes) > 0:
            for cur_routing in all_possible_routes.copy():
                # add all existing connections
                all_next_conns = [cur_cnn for cur_cnn in setup_devices_cnns
                                  if ((cur_cnn.from_device == cur_routing.end_device and
                                       cur_cnn.from_node_name == cur_routing.end_node_name)
                                      or (cur_cnn.to_device == cur_routing.end_device and
                                          cur_cnn.to_node_name == cur_routing.end_node_name))]
                for cur_next_conn in all_next_conns:
                    if cur_next_conn == cur_routing.elements[-1]:
                        # is the same connection as the last of routing -> SKIP
                        continue
                    elif cur_next_conn.has_connection_from_to(start_device=cur_routing.end_device):
                        # the connection allows the direction the routing needs - only then add it
                        copied_routing = cur_routing.copy()
                        copied_routing.append_element(cur_next_conn)
                        all_possible_routes.append(copied_routing)
                # add all possible gateways
                # for cur_next_gateway in cur_routing.end_device._get_all_gateways():
                #     if cur_next_gateway == cur_routing.elements[-1]:
                #         # is the same gateway as the last one of the routing -> SKIP
                #         continue
                #     elif cur_next_gateway.has_connection_from_to(start_node=cur_routing.end_node_name):
                #         # the gateway allows the direction the routing needs - only then add it
                #         copied_routing = cur_routing.copy()
                #         copied_routing.append_element(cur_next_gateway)
                #         all_possible_routes.append(copied_routing)

            # remove all routings that have a loop
            for cur_routing in all_possible_routes.copy():
                if cur_routing.has_loop():
                    all_possible_routes.remove(cur_routing)

            # remove all routings which do not work because they have the wrong connection type
            for cur_routing in all_possible_routes.copy():
                # check that one part connection matches the requirements of the given `scenario_connection`
                found_possibility = False
                for cur_virtual_conn in cur_routing.get_virtual_connection():
                    if scenario_connection.contained_in(cur_virtual_conn, ignore_metadata=True):
                        # find one part of the virtual connection that matches the requirement
                        # -> do not delete this route
                        found_possibility = True
                if not found_possibility:
                    all_possible_routes.remove(cur_routing)

            # move all completely routed connections to `all_completed_routes`
            for cur_routing in all_possible_routes.copy():
                if cur_routing.end_device == to_setup_device:
                    # note that all routes already have a virtual connection that matches the requirements of given
                    # `scenario_connection`
                    all_completed_routes.append(cur_routing)
                    all_possible_routes.remove(cur_routing)

        return all_completed_routes

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def elements(self) -> List[Connection, NodeGateway]:
        return self._routing_elems

    @property
    def start_device(self) -> Type[Device]:
        return self._start_device

    @property
    def start_node_name(self) -> str:
        return self._start_node_name

    @property
    def end_device(self) -> Type[Device]:
        return self._get_end_device_and_node()[0]

    @property
    def end_node_name(self) -> str:
        return self._get_end_device_and_node()[1]

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _get_end_device_and_node(self) -> Tuple[Type[Device], str]:
        """helper method that determines the end_device and end_node_name"""
        cur_device = self._start_device
        cur_node_name = self._start_node_name

        for cur_route_elem in self._routing_elems:
            if isinstance(cur_route_elem, NodeGateway):
                if cur_node_name == cur_route_elem.from_node_name:
                    cur_node_name = cur_route_elem.to_node_name
                elif cur_node_name == cur_route_elem.to_node_name:
                    cur_node_name = cur_route_elem.from_node_name
                else:
                    raise RoutingBrokenChainError(
                        f"can not chain the routing element `{cur_route_elem.__name__}` with the device "
                        f"`{cur_device.__name__}` and node `{cur_node_name}` of element before")
            else:
                if cur_node_name == cur_route_elem.from_node_name and cur_device == cur_route_elem.from_device:
                    cur_node_name = cur_route_elem.to_node_name
                    cur_device = cur_route_elem.to_device
                elif cur_node_name == cur_route_elem.to_node_name and cur_device == cur_route_elem.to_device:
                    cur_node_name = cur_route_elem.from_node_name
                    cur_device = cur_route_elem.from_device
                else:
                    raise RoutingBrokenChainError(
                        f"can not chain the routing element `{cur_route_elem.__name__}` with the device "
                        f"`{cur_device.__name__}` and node `{cur_node_name}` of element before")
        return cur_device, cur_node_name

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def has_loop(self):
        """
        This method returns True if it detects an internal loop. An internal loop is given, if one :class:`Device`
        is mentioned twice (or more) in internal `routing_elements` while both elements are arriving at the same node of
        this device.
        """
        all_devices = []
        all_nodes = []
        for cur_elem in self._routing_elems:
            if isinstance(cur_elem, NodeGateway):
                all_devices.append(cur_elem.device)
                all_nodes.append(cur_elem.from_node_name)
            else:
                # :class:`balder.Connection`
                all_devices.append(cur_elem.from_device)
                all_nodes.append(cur_elem.from_node_name)
        if len(self._routing_elems) > 0:
            last_elem = self._routing_elems[-1]
            if isinstance(last_elem, NodeGateway):
                all_devices.append(last_elem.device)
                all_nodes.append(last_elem.to_node_name)
            else:
                # :class:`balder.Connection`
                all_devices.append(last_elem.to_device)
                all_nodes.append(last_elem.to_node_name)

    def is_bidirectional(self):
        """
        This method checks whether the route is completely bidirectional. If only one connection is not bidirectional,
        it will return False.
        """
        for cur_elem in self._routing_elems:
            if isinstance(cur_elem, Connection):
                if not cur_elem.is_bidirectional():
                    return False
            else:
                if not cur_elem.is_bidirectional():
                    return False
        return True

    def copy(self) -> RoutingPath:
        """
        This method creates a copy of this routing.
        """
        return copy.copy(self)

    def append_element(self, elem: Union[Connection, NodeGateway]) -> None:
        """
        This method appends an element to the route.
        """
        elem_before = None if len(self._routing_elems) == 0 else self._routing_elems[-1]

        if not isinstance(elem, Connection) and not isinstance(elem, NodeGateway):
            raise TypeError(f"the given attribute passed at position {len(self._routing_elems)} is not of the type "
                            f"`Connection` or `NodeGateway`")

        if elem_before is not None:
            # check if device and nodes of the two elements are the same -> have to be a chain
            if isinstance(elem_before, Connection):
                before_device = elem_before.to_device
                before_node_name = elem_before.to_node_name
            else:
                # is a gateway class
                before_device = elem_before.device
                before_node_name = elem_before.to_node_name

            if isinstance(elem, Connection):
                cur_device = elem.from_device
                cur_node_name = elem.from_node_name
            else:
                # is a gateway class
                cur_device = elem.device
                cur_node_name = elem.from_node_name
            if before_device != cur_device:
                raise RoutingBrokenChainError(
                    f"the to-device of the transferred element at position {len(self._routing_elems) - 1} "
                    f"(`{before_device.__name__}`) does not match the from-device of the transferred element at "
                    f"position {len(self._routing_elems)} (`{cur_device.__name__}`)")
            if before_node_name != cur_node_name:
                raise RoutingBrokenChainError(
                    f"the to-device node name of the transferred element at position {len(self._routing_elems) - 1} "
                    f"(`{before_device.__name__}`) does not match the from-device node name of the transferred element "
                    f"at position {len(self._routing_elems)} (`{cur_device.__name__}`)")

        self._routing_elems.append(elem)

    def get_virtual_connection(self) -> List[Connection]:
        """
        This method returns a virtual connection object that describes the connection type this routing
        supports for all of its elements.
        """
        virtual_connection = [self.elements[0]]
        for cur_element in self.elements[1:]:
            if isinstance(cur_element, Connection):
                virtual_connection = cur_element.intersection_with(virtual_connection)
            else:
                # is a gateway class
                # todo
                pass
        return virtual_connection
