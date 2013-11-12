#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from time import sleep

import virtualbox as _virtualbox

from candelabra.topology.network import NetworkNode
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)


class VirtualboxNetworkNode(NetworkNode):
    """ A VirtualBox network
    """

    __known_attributes = {
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a network node
        """
        super(VirtualboxNetworkNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

    @property
    def machine(self):
        return self._container

    def do_network_create(self):
        logger.debug('network create: nothing to do')

        #try:
        #    logger.info('... creating NAT')
        #    network = self._vbox.create_nat_network(NAT_NETWORK)
        #    network.enabled = True
        #    logger.info('...... name: %s', network.network_name)
        #    logger.info('...... net: %s', network.network)
        #except _virtualbox.library.VBoxErrorIprtError, e:
        #    logger.warning(str(e))

        # get the maximum number of adapters
        #properties = self._vbox.system_properties
        ##properties.get_max_network_adapters()

    def do_network_up(self):
        logger.debug('network up: nothing to do')

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        """ The representation
        """
        extra = []
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_uuid:
            extra += ['uuid:%s' % self.cfg_uuid]
        if self.cfg_scope:
            extra += ['scope=%s' % self.cfg_scope]

        return "<VirtualboxNetwork(%s) at 0x%x>" % (','.join(extra), id(self))
