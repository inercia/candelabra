#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

import virtualbox as _virtualbox
from candelabra.errors import MachineNetworkSetupException

from candelabra.topology.network import NetworkNode
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)


class VirtualboxNetworkNode(NetworkNode):
    """ A VirtualBox network
    """

    __known_attributes = [
    ]

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a network node
        """
        super(VirtualboxNetworkNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # private attributes
        self._dhcp_server = None

    @property
    def machine(self):
        return self._container

    def do_network_create(self):
        if self.is_nat:
            logger.debug('network create: nothing to do for VirtualBox network %s', self.cfg_name)
        else:
            logger.info('setting up DHCP server for network "%s"', self.cfg_name)
            try:
                self._dhcp_server = self.machine._vbox.find_dhcp_server_by_network_name(self.cfg_name)
                if not self._dhcp_server:
                    logger.debug('creating DHCP server for network "%s"', self.cfg_name)
                    self._dhcp_server = self.machine._vbox.create_dhcp_server(self.cfg_name)

                self._dhcp_server.set_configuration(self.cfg_dhcp_server_ip.format(num=self._num),
                                                    self.cfg_netmask,
                                                    self.cfg_dhcp_start.format(num=self._num),
                                                    self.cfg_dhcp_end.format(num=self._num))
                self._dhcp_server.enabled = True

                logger.debug('... [%s] ip:%s mask:%s',
                             self._dhcp_server.network_name,
                             self._dhcp_server.ip_address,
                             self._dhcp_server.network_mask)
                self._dhcp_server.start(self.cfg_name,
                                        trunk_name='',
                                        trunk_type='')

            except _virtualbox.library.VBoxError, e:
                raise MachineNetworkSetupException('could not create DHCP server: %s' % str(e))

    def do_network_up(self):
        logger.debug('network up: nothing to do for VirtualBox network %s', self.cfg_name)

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        """ The representation
        """
        extra = []
        extra += ['#%d' % self._num]
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_uuid:
            extra += ['uuid:%s' % self.cfg_uuid]
        if self.cfg_scope:
            extra += ['scope=%s' % self.cfg_scope]

        return "<VirtualboxNetwork(%s) at 0x%x>" % (','.join(extra), id(self))
