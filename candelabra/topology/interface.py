#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A network interface in the topology.

Network interfaces must belong to a Machine, so they must be contained in a :class:`MachineNode` instance.
"""

from logging import getLogger
from candelabra.errors import MalformedTopologyException

from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)

#: supported interface types
INTERFACE_TYPES = {
    'nat',
    'host-only',
}

#: how an interface can get an IP address
GET_IP_TYPES = {'dhcp', 'static'}

#: default interfaces that will be added if nothing is specified...
DEFAULT_INTERFACES = [
    {
        'type': 'nat',
        'ip': 'automatic',
    }
]


class InterfaceNode(TopologyNode):
    """ A machine network interface

    Some important attributes:
    * the interface **type**, that can be 'nat', 'host-only', etc...
    * the **ip** address, that can be a numeric IP, a host name, or some reserved words like *automatic*
    * the interace name, **ifname**.
    """

    __known_attributes = {
        'type': TopologyAttribute(constructor=str, default='nat', inherited=True),
        'ip': TopologyAttribute(constructor=str, default='', inherited=True),
        'netmask': TopologyAttribute(constructor=str, default='', inherited=True),
        'ifname': TopologyAttribute(constructor=str, default='', inherited=True),
        'get_ip': TopologyAttribute(constructor=str, default='dhcp', inherited=True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a network interface in the machine
        """
        super(InterfaceNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # check the attributes
        if self.cfg_type:
            if not self.cfg_type in INTERFACE_TYPES:
                raise MalformedTopologyException('unkown interface type %s: should be one of %s',
                                                 self.cfg_type,
                                                 INTERFACE_TYPES)

        if self.cfg_get_ip not in GET_IP_TYPES:
            raise MalformedTopologyException('unknown method for getting an IP %s: should be one of %s',
                                             self.cfg_get_ip,
                                             GET_IP_TYPES)


    def do_iface_create(self):
        """ Create a network interface
        """
        logger.debug('interface create: nothing to do')
