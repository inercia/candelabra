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

#: how an interface can get an IP address
_SUPPORTED_IFACE_TYPES = {
    'dhcp',
    'static'
}


class InterfaceNode(TopologyNode):
    """ A machine network interface

    Some important attributes:
    * the interface **type**, that can be 'nat', 'host-only', etc...
    * the **ip** address, that can be a numeric IP, a host name, or some reserved words like *automatic*
    * the interace name, **ifname**.
    """

    __known_attributes = [
        TopologyAttribute('type', str, default='dhcp'),
        TopologyAttribute('ip', str, default=''),
        TopologyAttribute('netmask', str, default=''),
        TopologyAttribute('ifname', str, default=''),
        TopologyAttribute('connected', str, default=''),
    ]

    def __init__(self, **kwargs):
        """ Initialize a network interface in the machine
        """
        super(InterfaceNode, self).__init__(**kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # check the attributes
        if self.cfg_type not in _SUPPORTED_IFACE_TYPES:
            raise MalformedTopologyException('unknown interface type "%s": should be one of %s' % (
                self.cfg_type, _SUPPORTED_IFACE_TYPES))

        if not self.cfg_connected:
            raise MalformedTopologyException('interfaces must be "connected" to some network')

        # get the network this interface is connected to, but as a NetworkNode (or subclass) instance
        network = self.machine.get_network_by_name(self.cfg_connected)
        if not network:
            raise MalformedTopologyException('interface "%s" is connected to unknown network "%s"' %
                                             (self.cfg_name, self.cfg_connected))
        self.cfg_connected = network

        # private attributes
        self._num = self.get_inc_counter(self.machine, "cfg_interfaces")
        self._created = False

    #####################
    # tasks
    #####################

    def do_iface_create(self):
        """ Create a network interface
        """
        logger.debug('interface create: nothing to do #%d', self._num)

    def do_iface_up(self):
        """ Setup the network interface
        """
        logger.debug('interface setup: nothing to do for #%d', self._num)

    #####################
    # properties
    #####################

    @property
    def machine(self):
        """ Return the machine where this insterface s installed
        :returns: a :class:`MachineNode`: instance
        """
        return self._container

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        extra = []
        extra += ['#%d' % self._num]
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_class:
            extra += ['class:%s' % self.cfg_class]
        if self.cfg_connected:
            extra += ['connected-to:%s' % self.cfg_connected.cfg_name]

        return "<%s(%s) at 0x%x>" % (self.__class__.__name__, ','.join(extra), id(self))


