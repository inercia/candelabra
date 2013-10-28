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

    _known_attributes = {
        'hostname': 'the hostname',
        'interfaces': 'the interface',
        'provisioner': 'the provisioner',
        'shared': 'shared folders',
    }

    def __init__(self, dictionary, parent=None):
        """ Initialize a machines definition
        """
        super(Machine, self).__init__(dictionary, parent)

        # get some attributes
        self._settattr_dict_defaults(dictionary, self._known_attributes)

    #####################
    # tasks
    #####################

    def get_tasks_up(self):
        return []

    #####################
    # auxiliary
    #####################

    def __str__(self):
        """ Return a string representation for this machine
        """
        provisioner = getattr(self, 'provisioner', '')
        interfaces = getattr(self, 'interfaces', [])
        shared = getattr(self, 'shared', [])

        return super(Machine, self).__str__() + \
               ' provisioner:%s ifaces:%d shared:%d' % (provisioner, len(interfaces), len(shared))

