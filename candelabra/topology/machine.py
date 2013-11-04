#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

"""
A machine in a topology.
"""

from logging import getLogger

from candelabra.config import config
from candelabra.constants import CFG_DEFAULT_PROVIDER
from candelabra.errors import MalformedTopologyException, MissingBoxException
from candelabra.topology.box import BoxNode
from candelabra.topology.node import TopologyNode, TopologyAttribute


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

from candelabra.plugins import build_shared_instance, build_provisioner_instance, build_interface_instance


class MachineNode(TopologyNode):
    """ A machine in the toplogy hierarchy.

    There are two important classes of machines:

    * the global machine, a machine used for storing global attributes.
    * regular machines.
    """

    __known_attributes = {
        'box': TopologyAttribute(constructor=BoxNode, inherited=True),
        'hostname': TopologyAttribute(constructor=str, default='', inherited=True),
        'interfaces': TopologyAttribute(constructor=build_interface_instance, default=[], copy=True),
        'provisioner': TopologyAttribute(constructor=build_provisioner_instance, default=[], copy=True),
        'shared': TopologyAttribute(constructor=build_shared_instance, default=[], copy=True),
    }

    __state_attributes = {
        'state'
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a machines definition
        """
        super(MachineNode, self).__init__(_parent=_parent, **kwargs)

        # set the default class for nodes if it has not been set
        if not self.cfg_class:
            self.cfg_class = config.get_key(CFG_DEFAULT_PROVIDER)
            logger.debug('using default node class: %s', self.cfg_class)

        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

    #####################
    # state
    #####################

    def get_state_dict(self):
        """ Get current state as a dictionary, suitable for saving in a state file
        """
        local_dict = {}
        super_dict = super(MachineNode, self).get_state_dict()
        try:
            for attr in self.__state_attributes:
                v = getattr(self, 'cfg_' + attr, None)
                if v:
                    if hasattr(v, 'get_state_dict'):
                        local_dict[attr] = v.get_state_dict()
                    else:
                        local_dict[attr] = v
            super_dict.update(local_dict)
        except AttributeError:
            pass
        return super_dict

    def get_state(self):
        """ Return the machine current state
        """
        return STATE_UNKNOWN[0]

    def get_state_str(self):
        """ Return the machine current state
        """
        return STATE_TO_STR[self.get_state()]

    state = property(lambda self: self.get_state())
    state_str = property(lambda self: self.get_state_str())

    is_unknown = property(lambda self: self.get_state() == STATE_UNKNOWN[0],
                          doc='True if the machine is in unknown state')
    is_running = property(lambda self: self.get_state() == STATE_RUNNING[0],
                          doc='True if the machine is running')
    is_powered_down = property(lambda self: self.get_state() == STATE_POWERDOWN[0],
                               doc='True if the machine is powered down')
    is_aborted = property(lambda self: self.get_state() == STATE_ABORTED[0],
                          doc='True if the machine is aborted')
    is_starting = property(lambda self: self.get_state() == STATE_STARTING[0],
                           doc='True if the machine is starting')
    is_stopping = property(lambda self: self.get_state() == STATE_STOPPING[0],
                           doc='True if the machine is stopping')

    #####################
    # tasks: sched
    #####################

    def get_tasks_up(self):
        """ Get the tasks needed for the command "up"
        """
        if not self.cfg_name:
            raise MalformedTopologyException('missing attribute in topology: the virtual machine has no "name"')

        self.clear_tasks()

        logger.debug('checking if the machine "%s" exists', self.cfg_name)
        if self.cfg_uuid and self.machine:
            logger.info('... %s seems to have been already created', self.machine)
        else:
            logger.info('"%s" does not seem to exist', self.cfg_name)
            logger.info('... will import it from %s appliance "%s"', self.cfg_class, self.cfg_box.cfg_name)
            if self.cfg_box.missing:
                logger.debug('... box "%s" must be downloaded first', self.cfg_name)
                self.add_task_seq(self._box_instance.do_download)

            self.add_task_seq(self.do_copy_appliance)

        if self.is_running:
            logger.info('machine %s seems to be running', self.cfg_name)
        else:
            for iface in self.cfg_interfaces:
                self.add_task_seq(iface.do_create)

            self.add_task_seq(self.do_power_up)

        for shared_folder in self.cfg_shared:
            self.add_task_seq(shared_folder.do_install)

        self.add_task_seq(self.do_create_guest_session)

        for shared_folder in self.cfg_shared:
            self.add_task_seq(shared_folder.do_mount)

        return self.get_tasks()

    def get_tasks_down(self):
        """ Get the tasks needed for the command "down"
        """
        self.clear_tasks()
        if not self.is_powered_down:
            self.add_task_seq(self.do_power_down)
        else:
            logger.info('machine %s is not running', self.cfg_name)
        return self.get_tasks()

    def get_tasks_pause(self):
        """ Get the tasks needed for the command "pause"
        """
        self.clear_tasks()
        if self.is_running:
            self.add_task_seq(self.do_pause)
        else:
            logger.info('machine %s is not running', self.cfg_name)
        return self.get_tasks()

    def get_tasks_destroy(self):
        """ Get the tasks needed for the command "destroy"
        """
        self.clear_tasks()
        if self.is_running:
            self.add_task_seq(self.do_power_down)
        self.add_task_seq(self.do_destroy)
        return self.get_tasks()

    #####################
    # tasks
    #####################

    def do_power_up(self):
        """ Power up the machine via launch
        """
        raise NotImplementedError('not implemented')

    def do_power_down(self):
        """ Power down the machine via launch
        """
        raise NotImplementedError('not implemented')

    def do_pause(self):
        """ Pause the machine via launch
        """
        raise NotImplementedError('not implemented')

    def do_copy_appliance(self):
        """ Copy the appliance as a new virtual machine.
        """
        self._appliance = self.cfg_box.get_appliance(self.cfg_class)
        if not self._appliance:
            raise MissingBoxException('box "%s" does not have a %s appliance' % (self.cfg_box.cfg_name, self.cfg_class))

        self._appliance.import_to_machine(self)

    def do_create_guest_session(self):
        """ Create a guest session
        """
        raise NotImplementedError('not implemented')

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        """ Return a string representation for this machine
        """
        extra = []
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_class:
            extra += ['class:%s' % self.cfg_class]
        if self._parent is None:
            extra += ['global']

        return "<Machine(%s) at 0x%x>" % (','.join(extra), id(self))


