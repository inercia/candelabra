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

TEMPLATE_DHCP = """
#VAGRANT-BEGIN
# The contents below are automatically generated by Vagrant. Do not modify.
BOOTPROTO=dhcp
ONBOOT=yes
DEVICE=eth{iface}
#VAGRANT-END
"""

TEMPLATE_STATIC = """
#VAGRANT-BEGIN
# The contents below are automatically generated by Vagrant. Do not modify.
BOOTPROTO=none
IPADDR={ip}
NETMASK={natemask}
DEVICE=eth{iface}
PEERDNS=no
#VAGRANT-END
"""


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
        num_iface = getattr(self._container, '_num_ifaces_setup', 0)
        logger.info('setting up network device num:%d', num_iface)

        if self.machine.is_global:
            logger.warning('... trying to setup a network interface in a global machine!!')
            return

        try:
            sleep(1.0)
            session = self.machine.lock(lock_type='write')

            # create a mutable copy of the machine for doing changes...
            new_machine = session.machine
            adapter = new_machine.get_network_adapter(num_iface)

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
            adapter = self.machine.vbox_machine.get_network_adapter(num_iface)
            logger.info("...... [%d] MAC:%s family:%s enabled:%s",
                        adapter.slot,
                        adapter.mac_address,
                        adapter.adapter_type,
                        adapter.enabled)

            setattr(self._container, '_num_ifaces_setup', num_iface + 1)
            sleep(1.0)

    def do_iface_up(self):
        """ Setup the interface in the guest machine
        """
        iface = int(getattr(self._container, '_num_ifaces_setup', 0))
        logger.info('setting up network device num:%d', iface)

        # Accumulate the configurations to add to the interfaces file as
        # well as what interfaces we're actually configuring since we use that
        # later.
        scripts_dir = '/etc/sysconfig/network-scripts'

        # Render and upload the network entry file to a deterministic
        # temporary location.

        if self.cfg_type == 'dhcp':
            content = TEMPLATE_DHCP.format(iface=iface)
        elif self.cfg_type == 'static':
            content = TEMPLATE_STATIC.format(iface=iface)
        else:
            assert False

        logger.debug('saving template to temporal file...')
        self.machine.communicator.write_file(content, "/tmp/vagrant-network-entry_{iface}".format(iface=iface))

        # Remove any previous vagrant configuration in this network interface's
        # configuration files.
        COMMANDS = """
        touch {scripts_dir}/ifcfg-eth{iface}
        sed -e '/^#VAGRANT-BEGIN/,/^#VAGRANT-END/ d' {scripts_dir}/ifcfg-eth{iface} > /tmp/vagrant-ifcfg-eth{iface}
        cat /tmp/vagrant-ifcfg-eth{iface} > {scripts_dir}/ifcfg-eth{iface}
        rm -f /tmp/vagrant-ifcfg-eth{iface}
        /sbin/ifdown eth{iface} 2> /dev/null
        cat /tmp/vagrant-network-entry_{iface} >> {scripts_dir}/ifcfg-eth{iface}
        ARPCHECK=no /sbin/ifup eth{iface} 2> /dev/null
        rm -f /tmp/vagrant-network-entry_{iface}
        """
        self.machine.communicator.sudo_lines(COMMANDS, iface=iface, scripts_dir=scripts_dir)

        setattr(self._container, '_num_ifaces_setup', iface + 1)
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

        if self.cfg_connected and isinstance(self.cfg_connected, NetworkNode):
            extra += ['connected-to:%s' % self.cfg_connected.cfg_name]

        return "<VirtualboxInterface(%s) at 0x%x>" % (','.join(extra), id(self))
