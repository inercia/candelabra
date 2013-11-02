#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import os
from logging import getLogger
from candelabra.boxes import BoxesStorage

from candelabra.errors import UnsupportedBoxException, ImportException

logger = getLogger(__name__)


class VirtualboxAppliance(object):
    """ A VirtualBox appliance
    """
    provider = 'virtualbox'

    def __init__(self, path):
        """ Initialize a virtualbox box
        :param path: the OVF file
        """
        self.ovf = path

    @staticmethod
    def is_valid(folder):
        """ Return True if the folder contains a valid VirtualBox template
        """
        ovf_file = os.path.join(folder, 'box.ovf')
        return os.path.isfile(ovf_file)

    @staticmethod
    def from_dir(folder):
        """ Obtain a VirtualboxBox appliance from a directory
        :raises UnsupportedBoxException: if there is no valid VirtualboxBox found at that directory
        """
        ovf_file = os.path.join(folder, 'box.ovf')
        if os.path.isfile(ovf_file):
            return VirtualboxAppliance(path=ovf_file)
        else:
            raise UnsupportedBoxException('OVF file not found at %s' % ovf_file)

    def copy_to_virtualbox(self, node):
        """ Copy (import) the appliance to VirtualBox
        """
        logger.info('importing appliance from /%s as "%s"', BoxesStorage.get_relative_path(self.ovf), node.cfg_name)

        import virtualbox
        vbox = virtualbox.VirtualBox()

        appliance = vbox.create_appliance()
        progress = appliance.read(self.ovf)
        progress.wait_for_completion(-1)
        appliance.interpret()

        logger.info('... importing the machines')
        progress = appliance.import_machines([])
        logger.info('... waiting for import to finish')
        progress.wait_for_completion(-1)

        if len(appliance.machines) > 0:
            machine_uuid = appliance.machines[0]
            node.cfg_uuid = machine_uuid
            logger.debug(node.get_info())
        else:
            raise ImportException('no virtual machine created after import of %s' % node.cfg_name)

    #####################
    # auxiliary
    #####################
    def __repr__(self):
        """ The representation
        """
        return "<VirtualboxBox at 0x%x>" % (id(self))

