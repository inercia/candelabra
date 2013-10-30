#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.node import TopologyNode


logger = getLogger(__name__)


# the virtual machine state
STATE_RUNNING = (0, 'running')
STATE_PAUSED = (1, 'paused')
STATE_ABORTED = (2, 'aborted')
STATE_POWERDOWN = (3, 'powerdown')
STATE_STARTING = (4, 'starting')
STATE_STOPPING = (5, 'stopping')
STATE_UNKNOWN = (1000, 'unknown')

STATES_ALL = [STATE_RUNNING, STATE_PAUSED, STATE_ABORTED, STATE_POWERDOWN, STATE_STARTING, STATE_STOPPING,
              STATE_UNKNOWN]

STATE_TO_STR = {k: v for k, v in STATES_ALL}
STR_TO_STATE = {v: k for k, v in STATES_ALL}

########################################################################################################################


class Machine(TopologyNode):
    """ A machine
    """

    hostname = None
    interfaces = []

    _KNOWN_ATTRIBUTES = {
        'box': 'the box',
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
        self._settattr_dict_defaults(dictionary, self._KNOWN_ATTRIBUTES)

    #####################
    # state
    #####################

    def get_state_dict(self):
        """ Get current state as a dictionary, suitable for saving in a state file
        """
        return {
            'class': str(self.cfg_class),
            'name': str(self.cfg_name),
            'uuid': str(self.uuid),
            'state': str(self.state_str),
        }

    @property
    def state(self):
        """ Return the machine current state
        """
        return STATE_UNKNOWN[0]

    @property
    def state_str(self):
        """ Return the machine current state (as an string)
        """
        return STATE_TO_STR[self.state]

    @property
    def is_running(self):
        return bool(self.state == STATE_RUNNING[0])

    @property
    def is_powered_down(self):
        return bool(self.state == STATE_POWERDOWN[0])

    @property
    def is_starting(self):
        return bool(self.state == STATE_STARTING[0])

    @property
    def is_stopping(self):
        return bool(self.state == STATE_STOPPING[0])

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
        provisioner = getattr(self, 'cfg_provisioner', '')
        interfaces = getattr(self, 'cfg_interfaces', [])
        shared = getattr(self, 'cfg_shared', [])

        return super(Machine, self).__str__() + \
               ' provisioner:%s ifaces:%d shared:%d' % (provisioner, len(interfaces), len(shared))

