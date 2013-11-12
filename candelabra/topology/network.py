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

#: default networks
DEFAULT_NETWORKS = [
    {
        'name': 'nat',
        'scope': 'nat',
    }
]

class NetworkNode(TopologyNode):
    """ A network

    Some important attributes:
    * the network **scope**, that can be 'nat', 'private', etc...
    * the **netmask**
    """

    __known_attributes = {
        'scope': TopologyAttribute(constructor=str, default='nat', inherited=True),
        'netmask': TopologyAttribute(constructor=str, default='255,255.255.0', inherited=True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a network
        """
        super(NetworkNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # check the attributes
        if self.cfg_scope:
            if not self.cfg_scope in SUPPORTED_SCOPES:
                raise MalformedTopologyException('unknown network scope "%s": should be one of %s',
                                                 self.cfg_scope,
                                                 SUPPORTED_SCOPES)

        # private attributes
        self._created = False

    def do_network_create(self):
        logger.debug('network create: nothing to do')

    def do_network_up(self):
        logger.debug('network up: nothing to do')