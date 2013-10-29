#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

import vbox

from candelabra.constants import VIRTUALBOX_EXTRA_PATHS, DEFAULT_CFG_SECTION_VIRTUALBOX
from candelabra.errors import ProviderNotFoundException
from candelabra.topology.machine import Machine
from candelabra.config import config

logger = getLogger(__name__)


class VirtualboxMachine(Machine):
    """ A VirtualBox machine
    """

    _known_attributes = {
        'path': 'the virtual machine image path',
    }

    def __init__(self, dictionary, parent=None):
        """ Initialize a VirtualBox machine
        """
        super(VirtualboxMachine, self).__init__(dictionary, parent)

        self._settattr_dict_defaults(dictionary, self._known_attributes)

        try:
            # create a reference to the API
            self.vbox = vbox.VBox(VIRTUALBOX_EXTRA_PATHS, debug=True)
        except vbox.exceptions.VirtualBoxNotFound, e:
            m = 'could not find VirtualBox: %s' % str(e)
            logger.critical(m)
            raise ProviderNotFoundException(m)

        self.vm = None

        if config.has_section(DEFAULT_CFG_SECTION_VIRTUALBOX):
            self.cfg = config.items(section=DEFAULT_CFG_SECTION_VIRTUALBOX)
            if len(self.cfg) > 0:
                logger.debug('VirtualBox default config:')
                for k, v in self.cfg:
                    logger.debug('   %s = %s', k, v)
        else:
            self.cfg = None

    #####################
    # tasks
    #####################

    def get_tasks_up(self):
        #return [(self.do_get_vms_registered, )]
        return []

    def do_get_vms_registered(self):
        for machine in self.vbox.bound.vms.listRegistered():
            logger.debug('Machine info:')
            for k, v in machine.info.iteritems():
                logger.debug('  %s = %s', k, v)

    def do_load_vm(self):
        """ Load the VM
        """
        try:
            self.vm = self.vbox.api.vms.getOrCreate(self.name)
        except vbox.bound.exceptions.VmNotFound, e:
            logger.warning('virtual machine %s not found: %s', self.name, str(e))

    def do_create_hd(self, size):
        """ Create a HD
        """
        hdd = self.vbox.api.hdds.create(size=size)
        logger.debug('created HD with uuid=%s', hdd.UUID)
        return hdd

    def do_destroy_hd(self, uuid):
        hdd.destroy()

    def do_destroy(self):
        """ Destroy the VM
        """
        if self.vm:
            self.vm.destroy()

