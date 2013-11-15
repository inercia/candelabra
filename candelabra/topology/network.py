#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A network in the topology.
"""

from logging import getLogger
from candelabra.errors import MalformedTopologyException

from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)

#: supported network types
SUPPORTED_SCOPES = {
    'nat',
    'private',
}


class NetworkNode(TopologyNode):
    """ A network

    Some important attributes:
    * the network **scope**, that can be 'nat', 'private', etc...
    * the **netmask**
    """

    __known_attributes = {
        TopologyAttribute('scope', str, default='nat'),
        TopologyAttribute('netmask', str, default='255,255.255.0'),

        TopologyAttribute('dhcp_server_ip', str, default='10.10.{num}.1'),
        TopologyAttribute('dhcp_start', str, default='10.10.{num}.2'),
        TopologyAttribute('dhcp_end', str, default='10.10.{num}.255'),
    }

    def __init__(self, **kwargs):
        """ Initialize a network
        """
        super(NetworkNode, self).__init__(**kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # check the attributes
        if self.cfg_scope:
            if not self.cfg_scope in SUPPORTED_SCOPES:
                raise MalformedTopologyException('unknown network scope "%s": should be one of %s',
                                                 self.cfg_scope,
                                                 SUPPORTED_SCOPES)

        # private attributes
        self._num = self.get_inc_counter(self.machine, "cfg_networks")
        self._created = False

    def do_network_create(self):
        logger.debug('network create: nothing to do for network', self.cfg_name)

    def do_network_up(self):
        logger.debug('network up: nothing to do for network', self.cfg_name)

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
    # properties
    #####################

    is_nat = property(lambda self: self.cfg_scope == 'nat',
                      doc='Check if it is the NAT network')