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
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)


class VirtualboxInterfaceNode(InterfaceNode):
    """ A VirtualBox interface
    """

    __known_attributes = {
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(VirtualboxInterfaceNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

    @property
    def machine(self):
        return self._container.get_machine()

    def do_create(self):
        """ Setup the net
        """
        logger.info('starting network device')

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

        num_iface = getattr(self._container, '_num_ifaces_setup', 0)

        try:
            sleep(1.0)
            s = _virtualbox.Session()
            self.machine.lock_machine(s, _virtualbox.library.LockType.write)
            new_machine = s.machine

            adapter = new_machine.get_network_adapter(num_iface)

            if self.cfg_type == 'nat':
                adapter.attachment_type = _virtualbox.library.NetworkAttachmentType.nat
            elif self.cfg_type == 'host-only':
                adapter.attachment_type = _virtualbox.library.NetworkAttachmentType.host_only

            adapter.cable_connected = True
            adapter.enabled = True

            new_machine.save_settings()
            s.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineChangeException(str(e))
        else:
            adapter = self.machine.get_network_adapter(num_iface)
            logger.info("...... [%d] MAC:%s family:%s enabled:%s %s",
                        adapter.slot,
                        adapter.mac_address,
                        adapter.adapter_type,
                        adapter.enabled,
                        adapter.nat_network)

            setattr(self._container, '_num_ifaces_setup', num_iface + 1)
            sleep(1.0)

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
        if self.cfg_type:
            extra += ['type=%s' % self.cfg_type]

        return "<VirtualboxInterface(%s) at 0x%x>" % (','.join(extra), id(self))
