#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.node import TopologyNode


logger = getLogger(__name__)


class Machine(TopologyNode):
    """ A machine
    """

    hostname = None
    interfaces = []

    def __init__(self, dictionary, parent=None):
        """ Initialize a machines definition
        """
        super(Machine, self).__init__(dictionary, parent)

        # get some attributes
        # it is important to NOT SET the attribute if not found in the dictionary, so it will inherit from its father
        if 'hostname' in dictionary:
            self.hostname = dictionary["hostname"]

        if 'interfaces' in dictionary:
            self.interfaces = dictionary["interfaces"]

        if 'provisioner' in dictionary:
            self.provisioner = dictionary["provisioner"]

        if 'shared' in dictionary:
            self.shared = dictionary["shared"]

    def __str__(self):
        return super(Machine, self).__str__() + \
               ' provisioner:%s ifaces:%d shared:%d' % (self.provisioner, len(self.interfaces), len(self.shared))