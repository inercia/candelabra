#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from time import sleep

import virtualbox as _virtualbox

from candelabra.errors import MachineChangeException
from candelabra.topology.interface import InterfaceNode
from candelabra.topology.network import NetworkNode
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)


class VirtualboxInterfaceNode(InterfaceNode):
    """ A VirtualBox interface
    """

    __known_attributes = [
    ]

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(VirtualboxInterfaceNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        if not self.cfg_connected:
            logger.warning('interface is not connected')

        from .network import VirtualboxNetworkNode
        assert isinstance(self.cfg_connected, VirtualboxNetworkNode)

    @property
    def machine(self):
        return self._container

    def do_iface_create(self):
        """ Setup the net
        """
        logger.info('creating network interface #%d', self._num)
        logger.debug('... connected to %s', self.cfg_connected.cfg_name)

        if self.machine.is_global:
            logger.warning('... trying to setup a network interface in a global machine!!')
            return

        try:
            sleep(1.0)
            session = self.machine.lock(lock_type='write')

            # create a mutable copy of the machine for doing changes...
            new_machine = session.machine
            adapter = new_machine.get_network_adapter(self._num)

            if self.cfg_type == 'nat':
                logger.info('... type: NAT')
                adapter.attachment_type = _virtualbox.library.NetworkAttachmentType.nat
            elif self.cfg_connected.cfg_scope == 'private':
                logger.info('... type: private')
                adapter.attachment_type = _virtualbox.library.NetworkAttachmentType.internal
                adapter.internal_network = self.cfg_connected.cfg_name

            adapter.cable_connected = True
            adapter.enabled = True

            # save the new machine and unlock it
            new_machine.save_settings()
            self.machine.unlock(session)
        except _virtualbox.library.VBoxError, e:
            raise MachineChangeException(str(e))
        else:
            adapter = self.machine.vbox_machine.get_network_adapter(self._num)
            logger.info("...... [%d] MAC:%s family:%s enabled:%s",
                        adapter.slot,
                        adapter.mac_address,
                        adapter.adapter_type,
                        adapter.enabled)
            sleep(1.0)

    def do_iface_up(self):
        """ Setup the interface in the guest machine
        """
        logger.info('setting up network interface #%d', self._num)
        self.machine.guest.setup_iface(self._num, type=self.cfg_type, ip=self.cfg_ip, netmask=self.cfg_netmask)
        sleep(1.0)

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
        if self.cfg_type:
            extra += ['type=%s' % self.cfg_type]

        if self.cfg_connected and isinstance(self.cfg_connected, NetworkNode):
            extra += ['connected-to:%s' % self.cfg_connected.cfg_name]

        return "<VirtualboxInterface(%s) at 0x%x>" % (','.join(extra), id(self))
