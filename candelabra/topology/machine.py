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

from candelabra.plugins import build_shared_instance, build_provisioner_instance, build_interface_instance, build_network_instance


class MachineNode(TopologyNode):
    """ A machine in the topology hierarchy.

    There are two important classes of machines:

    * the global machine, a machine used for storing global attributes.
    * regular machines.

    Machines have some important attributes:

    * communicator: a :class:`Communicator` instance, used for communicating with the machine.
    * guest: a :class:`Guest` instance, used for running some standard commands in the machine.
    """

    __known_attributes = [
        TopologyAttribute('box', BoxNode),
        TopologyAttribute('hostname', str, default=''),
        TopologyAttribute('networks', build_network_instance),
        TopologyAttribute('interfaces', build_interface_instance, default=[], copy=True, append=True),
        TopologyAttribute('provisioners', build_provisioner_instance, default=[], copy=True),
        TopologyAttribute('shared', build_shared_instance, default=[], copy=True),
    ]

    __state_attributes = {
        'state'
    }

    def __init__(self, **kwargs):
        """ Initialize a machines definition
        """
        super(MachineNode, self).__init__(**kwargs)

        # set the default class for nodes if it has not been set
        if not self.cfg_class:
            self.cfg_class = config.get_key(CFG_DEFAULT_PROVIDER)
            logger.debug('using default node class: %s', self.cfg_class)

        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        self.guest = None
        self.communicator = None

        # validate the attributes
        if not self.cfg_name and not self.is_global:
            raise MalformedTopologyException('machines must have a name')

    is_global = property(lambda self: self._parent is None, doc='True if this is the global node')

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
    # properties
    #####################

    def get_communicator_ip(self):
        """ Get the IP where a communicator can connect to
        """
        return None

    communicator_ip = property(lambda self: self.get_communicator_ip(),
                               doc='get an IP where the communicator can connect to')

    def get_network_by_name(self, name):
        """ Get a network given a name
        """
        for network in self.cfg_networks:
            if network.cfg_name == name:
                return network
        return None

    #####################
    # tasks: sched
    #####################

    def get_tasks_up(self):
        """ Get the tasks needed for the command "up"
        """
        if not self.cfg_name:
            raise MalformedTopologyException('missing attribute in topology: the virtual machine has no "name"')

        logger.debug('checking if the machine "%s" exists', self.cfg_name)
        if self.cfg_uuid:
            logger.info('... %s seems to have been already created', self.cfg_name)
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
            for network in self.cfg_networks:
                self.add_task_seq(network.do_network_create)
            for iface in self.cfg_interfaces:
                self.add_task_seq(iface.do_iface_create)

            self.add_task_seq(self.do_power_up)

        self.add_task_seq(self.do_wait_userland)

        # once we have the userland tools, detect the host type and create a guest reference
        self.add_task_seq(self.do_create_guest_reference)

        # create the shared folders
        for shared_folder in self.cfg_shared:
            self.add_task_seq(shared_folder.do_shared_create)

        # startup the networks/interfaces
        for network in self.cfg_networks:
            self.add_task_seq(network.do_network_up)
        for iface in self.cfg_interfaces:
            self.add_task_seq(iface.do_iface_up)

        # mount the shared folders
        for shared_folder in self.cfg_shared:
            self.add_task_seq(shared_folder.do_shared_mount)

    def get_tasks_down(self):
        """ Get the tasks needed for the command "down"
        """
        if not (self.is_unknown or self.is_powered_down):
            self.add_task_seq(self.do_power_down)
            self.add_task_seq(self.do_close_guest_sessions)
        else:
            logger.info('machine %s is not running', self.cfg_name)

    def get_tasks_pause(self):
        """ Get the tasks needed for the command "pause"
        """
        if self.is_running:
            self.add_task_seq(self.do_pause)
        else:
            logger.info('machine %s is not running', self.cfg_name)

    def get_tasks_destroy(self):
        """ Get the tasks needed for the command "destroy"
        """
        self.get_tasks_down()
        self.add_task_seq(self.do_destroy)

    def get_tasks_net_up(self):
        """ Get the tasks needed for the command "net up"
        """
        if self.is_running:
            logger.info('machine %s seems to be running', self.cfg_name)

            self.add_task_seq(self.do_wait_userland)

            # once we have the userland tools, detect the host type and create a guest reference
            self.add_task_seq(self.do_create_guest_reference)

            for network in self.cfg_networks:
                self.add_task_seq(network.do_network_up)
            for iface in self.cfg_interfaces:
                self.add_task_seq(iface.do_iface_up)
        else:
            logger.error('machine %s is not running!', self.cfg_name)
            logger.error('... it must be running for this command (it will not be started automatically)')

    def get_tasks_net_show(self):
        """ Get the tasks needed for the command "net show"
        """
        if self.is_running:
            logger.info('machine %s seems to be running', self.cfg_name)
            # TODO: not implemented yet
        else:
            logger.error('machine %s is not running!', self.cfg_name)
            logger.error('... it must be running for this command (it will not be started automatically)')

    #####################
    # tasks
    #####################

    def do_power_up(self):
        """ Power up the machine via launch
        """
        logger.debug('power up: nothing to do')

    def do_power_down(self):
        """ Power down the machine via launch
        """
        logger.debug('power down: nothing to do')

    def do_pause(self):
        """ Pause the machine via launch
        """
        logger.debug('pause: nothing to do')

    def do_copy_appliance(self):
        """ Copy the appliance as a new virtual machine.
        """
        self._appliance = self.cfg_box.get_appliance(self.cfg_class)
        if not self._appliance:
            raise MissingBoxException('box "%s" does not have a %s appliance' % (self.cfg_box.cfg_name, self.cfg_class))

        self._appliance.import_to_machine(self)

    def do_create_guest_reference(self):
        """ Create a guest reference
        """
        logger.debug('guest reference creation: nothing to do')

    def do_wait_userland(self):
        """ Wait for userland
        """
        logger.debug('wait userland: nothing to do')

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

    def pretty_print(self, prefix=''):
        logger.debug('%s %s', prefix, str(self))

        logger.debug('%s ... shared:', prefix)
        for s in self.cfg_shared:
            logger.debug('%s ...... %s', prefix, s)

        logger.debug('%s ... networks:', prefix)
        for n in self.cfg_networks:
            logger.debug('%s ...... %s', prefix, n)

        logger.debug('%s ... interfaces:', prefix)
        for i in self.cfg_interfaces:
            logger.debug('%s ...... %s', prefix, i)

        logger.debug('%s ... provisioners:', prefix)
        for p in self.cfg_provisioners:
            logger.debug('%s ...... %s', prefix, p)

