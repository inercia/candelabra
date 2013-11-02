#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from candelabra.topology.box import Box
from candelabra.topology.interface import Interface

from candelabra.topology.node import TopologyNode
from candelabra.topology.provisioner import Provisioner
from candelabra.topology.shared import Shared


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

    # known attributes
    # the right tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = {
        'box': Box,
        'hostname': str,
        'interfaces': Interface,
        'provisioner': Provisioner,
        'shared': Shared,
    }

    __state_attributes = {
        'state'
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a machines definition
        """
        super(Machine, self).__init__(_parent=_parent, **kwargs)
        self._settattr_dict_defaults(kwargs, self.__known_attributes)

    #####################
    # state
    #####################

    def get_state_dict(self):
        """ Get current state as a dictionary, suitable for saving in a state file
        """
        local_dict = {}
        super_dict = super(Machine, self).get_state_dict()
        try:
            for attr in self.__state_attributes:
                v = getattr(self, 'cfg_' + attr, None)
                if v:
                    local_dict[attr] = v
            super_dict.update(local_dict)
        except AttributeError:
            pass
        return super_dict

    def get_state(self):
        """ Return the machine current state
        """
        #return STATE_UNKNOWN[0]
        pass

    state = property(lambda self: self.get_state())

    state_str = property(lambda self: STATE_TO_STR[self.get_state()])

    is_unknown = property(lambda self: self.get_state() == STATE_UNKNOWN[0])
    is_running = property(lambda self: self.get_state() == STATE_RUNNING[0])
    is_powered_down = property(lambda self: self.get_state() == STATE_POWERDOWN[0])
    is_aborted = property(lambda self: self.get_state() == STATE_ABORTED[0])
    is_starting = property(lambda self: self.get_state() == STATE_STARTING[0])
    is_stopping = property(lambda self: self.get_state() == STATE_STOPPING[0])

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
        provisioner = getattr(self, 'cfg_provisioner', None)
        #interfaces = getattr(self, 'cfg_interfaces', None)
        #shared = getattr(self, 'cfg_shared', None)

        return super(Machine, self).__str__() + \
               ' provisioner:%s' % (    #ifaces:%d shared:%d' % (
                                        provisioner if provisioner else '') #,
        #len(interfaces) if interfaces else 0,
        #len(shared) if shared else 0)

