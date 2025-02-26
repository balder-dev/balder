from __future__ import annotations
from typing import List, Union, Dict, Type, Tuple, Iterable, TYPE_CHECKING

import copy
from _balder.connection import Connection
from _balder.node_gateway import NodeGateway
from _balder.controllers import DeviceController
from _balder.exceptions import RoutingBrokenChainError

if TYPE_CHECKING:
    from _balder.device import Device


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
            if self._start_device not in (first_elem.from_device, first_elem.to_device):
                raise ValueError(f"the given `start_device={self._start_device.__name__}` does not match with one of "
                                 f"the available devices of the first routing element")
            if self._start_node_name not in (first_elem.from_node_name, first_elem.to_node_name):
                raise ValueError(f"the given `start_node_name={self._start_node_name}` does not match with one of the "
                                 f"available node names of the first routing element")
        else:
            raise TypeError(f"the first given element is not an instance of `{Connection.__name__}` or "
                            f"`{NodeGateway.__name__}` (is `{type(first_elem)}`)")

        for cur_elem in routing_elems:
            self.append_element(cur_elem)

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def __get_abs_setup_dev_cnns_for(setup_devices: Iterable[Type[Device]]) -> List[Connection]:
        """
        Determines all absolute device connections for a given list of setup devices.
        """
        setup_devices_cnns = []
        for cur_setup_device in setup_devices:
            for cur_cnn_list in DeviceController.get_for(cur_setup_device).get_all_absolute_connections().values():
                setup_devices_cnns.extend(cur_cnn_list)
        # remove duplicates
        return list(set(setup_devices_cnns))

    @staticmethod
    def route_through(
            scenario_connection: Connection,
            device_mapping: Dict[Type[Device], Type[Device]],
            alternative_setup_device_cnns: Union[List[Connection], None] = None
    ) -> List[RoutingPath]:
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
            setup_devices_cnns = RoutingPath.__get_abs_setup_dev_cnns_for(device_mapping.values())

        from_setup_device = device_mapping[scenario_connection.from_device]
        to_setup_device = device_mapping[scenario_connection.to_device]

        # contains a list with all routes that start and end correctly
        all_completed_routes = []
        # contains a list with all possible routes
        all_possible_routes = []

        # add all connection objects that are mentioned in `from_setup_device`
        for cur_from_setup_node_conn in setup_devices_cnns:
            # only if there is a connection outgoing from `from_setup_device`
            if cur_from_setup_node_conn.has_connection_from_to(start_device=from_setup_device):
                all_possible_routes.append(
                    RoutingPath(
                        cur_from_setup_node_conn,
                        start_device=from_setup_device,
                        start_node_name=(cur_from_setup_node_conn.from_node_name
                                         if cur_from_setup_node_conn.from_device == from_setup_device
                                         else cur_from_setup_node_conn.to_node_name)
                    )
                )
        # now go through every possibility and add them - filter all Routes that ``has_loop() == True`` or
        # are completed
        while len(all_possible_routes) > 0:

            # remove all routings that have a loop
            all_possible_routes = [route for route in all_possible_routes.copy() if not route.has_loop()]

            # remove all not working routing because they have the wrong connection type, by checking that one part
            # connection matches the requirements of the given `scenario_connection`
            all_possible_routes = [
                r for r in all_possible_routes
                if scenario_connection.contained_in(r.get_virtual_connection(), ignore_metadata=True)
            ]

            # move all completely routed connections to `all_completed_routes`
            for cur_routing in all_possible_routes.copy():
                if cur_routing.end_device == to_setup_device:
                    # note that all routes already have a virtual connection that matches the requirements of given
                    # `scenario_connection`
                    all_completed_routes.append(cur_routing)
                    all_possible_routes.remove(cur_routing)

            new_possible_routes = []
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

                    if cur_next_conn.has_connection_from_to(start_device=cur_routing.end_device):
                        # the connection allows the direction the routing needs - only then add it
                        copied_routing = cur_routing.copy()
                        copied_routing.append_element(cur_next_conn)
                        new_possible_routes.append(copied_routing)
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
            all_possible_routes = new_possible_routes

        return all_completed_routes

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def elements(self) -> List[Union[Connection, NodeGateway]]:
        """returns all elements that belongs to this routing path"""
        return self._routing_elems

    @property
    def start_device(self) -> Type[Device]:
        """returns the device the route starts from"""
        return self._start_device

    @property
    def start_node_name(self) -> str:
        """returns the node of the `start_device` this route starts from"""
        return self._start_node_name

    @property
    def end_device(self) -> Type[Device]:
        """returns the device the route ends"""
        return self._get_end_device_and_node()[0]

    @property
    def end_node_name(self) -> str:
        """returns the node of the `end_device` this route ends"""
        return self._get_end_device_and_node()[1]

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _get_end_device_and_node(self, till_idx: int = None) -> Tuple[Type[Device], str]:
        """
        helper method that determines the end_device and end_node_name

        :param till_idx: the index of the latest element that should be considered

        :return: a tuple with the latest device and node
        """
        cur_device = self._start_device
        cur_node_name = self._start_node_name

        elements = self._routing_elems
        if till_idx is not None:
            elements = self._routing_elems[:till_idx+1]

        for cur_route_elem in elements:
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

    def has_loop(self) -> bool:
        """
        This method returns True if it detects an internal loop. An internal loop is given, if one :class:`Device`/node
        pair is mentioned twice (or more) in internal `routing_elements`.
        """
        all_contact_points = [(self.start_device, self.start_node_name)]

        for idx in range(len(self._routing_elems)):
            next_device, next_node = self._get_end_device_and_node(idx)
            # now check if one point is mentioned twice
            if (next_device, next_node) in all_contact_points:
                return True
            all_contact_points.append((next_device, next_node))

        return False

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
        copied_elem = copy.copy(self)
        # also copy list reference
        copied_elem._routing_elems = self._routing_elems.copy()  # pylint: disable=protected-access
        return copied_elem

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
            if isinstance(elem, Connection):
                if (self.end_device, self.end_node_name) not in \
                        [(elem.from_device, elem.from_node_name), (elem.to_device, elem.to_node_name)]:
                    raise RoutingBrokenChainError(
                        f"can not append connection, because neither the from-device/node "
                        f"(device: `{elem.from_device.__name__}` | node: `{elem.from_node_name}`) nor the "
                        f"to-device/node (device: `{elem.to_device.__name__}` | node: `{elem.to_node_name}`) of the "
                        f"connection match with the latest end-device/node (device: `{self.end_device.__name__}` | "
                        f"node: `{self.end_node_name}`) of this route")
            else:
                # is a gateway class
                if self.end_device != elem.device:
                    raise RoutingBrokenChainError(
                        f"can not append gateway, because the device of the gateway (`{elem.device}`) doesn't "
                        f"match with the latest end-device (`{self.end_device}`) of this route")
                if self.end_node_name not in [elem.from_node_name, elem.to_node_name]:
                    raise RoutingBrokenChainError(
                        f"can not append gateway, because neither the from-node "
                        f"(`{elem.from_node_name}`) nor the to-node (`{elem.to_node_name}`) of the gateway match with "
                        f"the latest end-node (`{self.end_node_name}`) of this route")

        self._routing_elems.append(elem)

    def get_virtual_connection(self) -> Connection:
        """
        This method returns a virtual connection object that describes the connection type this routing
        supports for all of its elements.
        """
        virtual_connection = self.elements[0].clone()
        virtual_connection.set_metadata_for_all_subitems(None)
        for cur_element in self.elements[1:]:
            if isinstance(cur_element, Connection):
                cur_element_clone = cur_element.clone()
                cur_element_clone.set_metadata_for_all_subitems(None)
                virtual_connection = cur_element_clone.intersection_with(virtual_connection)
            else:
                # is a gateway class
                # todo
                pass
        # set metadata based on this routing
        virtual_connection.metadata.set_from(from_device=self.start_device, from_device_node_name=self.start_node_name)
        virtual_connection.metadata.set_to(to_device=self.end_device, to_device_node_name=self.end_node_name)

        return virtual_connection
