#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from time import sleep

import virtualbox as _virtualbox

from candelabra.config import config
from candelabra.boxes import boxes_storage_factory
from candelabra.constants import DEFAULT_CFG_SECTION_VIRTUALBOX
from candelabra.errors import MissingBoxException, MalformedTopologyException, MachineChangeException
from candelabra.topology.machine import Machine
from candelabra.topology.machine import STATE_POWERDOWN, STATE_RUNNING, STATE_PAUSED, STATE_ABORTED, STATE_STARTING, STATE_STOPPING, STATE_UNKNOWN

logger = getLogger(__name__)

VIRTUALBOX_ST_TO_STATES = {
    # check _virtualbox.library.MachineState.running
    1: STATE_POWERDOWN,
    4: STATE_ABORTED,
    5: STATE_RUNNING,
    6: STATE_PAUSED,
    10: STATE_STARTING,
    11: STATE_STOPPING,
}


########################################################################################################################

_DEFAULT_POWER_UP_TIMEOUT = 5000
""" Default timeout while waiting for power up a machine
"""

_DEFAULT_POWER_DOWN_TIMEOUT = 5000
""" Default timeout while waiting for power down a machine
"""


########################################################################################################################


class VirtualboxMachine(Machine):
    """ A VirtualBox machine
    """

    # known attributed that can be provided in the configuration file
    _KNOWN_ATTRIBUTES = {
        'path': 'the virtual machine image path',
    }

    # attributes that are saved in the state file
    _STATE_ATTRIBUTES = {
        'uuid': 'the machine UUID',
        'state': 'the machine state'
    }

    def __init__(self, dictionary, parent=None):
        """ Initialize a VirtualBox machine
        """
        super(VirtualboxMachine, self).__init__(dictionary, parent)

        self._settattr_dict_defaults(dictionary, self._KNOWN_ATTRIBUTES)

        # get any VirtualBox default parameters from the config file
        if config.has_section(DEFAULT_CFG_SECTION_VIRTUALBOX):
            self._cfg = config.items(section=DEFAULT_CFG_SECTION_VIRTUALBOX)
            if len(self._cfg) > 0:
                logger.debug('VirtualBox default config:')
                for k, v in self._cfg:
                    logger.debug('... %s = %s', k, v)
                    setattr(self, 'default_' + k, v)
        else:
            self._cfg = None

        self._vbox = _virtualbox.VirtualBox()
        self._uuid = self.cfg_uuid if getattr(self, 'cfg_uuid', None) else None
        self._machine = None

    def sync_name(self):
        """ Set the VirtualBox virtual machine name to the same name as this node
        """
        logger.debug('synchronizing VM name: setting as %s', self.cfg_name)

        session = _virtualbox.Session()
        self.machine.lock_machine(session, _virtualbox.library.LockType.write)
        new_machine = session.machine

        try:
            new_machine.name = self.cfg_name
            new_machine.save_settings()
            session.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineChangeException(str(e))
        else:
            sleep(1.0)

    #####################
    # properties
    #####################

    def get_uuid(self):
        """ Get the machine UUID
        """
        return self._uuid

    def set_uuid(self, uuid):
        """ Set the machine UUID
        """
        self._uuid = uuid
        self._machine = None

    uuid = property(get_uuid, set_uuid)

    def get_machine(self):
        """ Get the underlying VirtualBox "machine" instance
        """
        if self._uuid and not self._machine:
            self._machine = self._vbox.find_machine(self._uuid)
            if self._machine.name != self.cfg_name:
                logger.warning('the configured name (%s) does not match the VM name (%s)',
                               self.cfg_name, self._machine.name)
        return self._machine

    machine = property(get_machine)

    def get_info(self):
        """ Get some machine information
        """
        return 'name: %s UUID:%s ' % (self.cfg_name, self.uuid) + \
               'CPUs:%d (exec-cap:%d) ' % (self.machine.cpu_count, self.machine.cpu_execution_cap) + \
               'mem:%d vram:%d ' % (self.machine.memory_size, self.machine.vram_size) + \
               'state:%s ' % (str(self.machine.state))

    @property
    def state(self):
        """ Get the VirtualBox machine state, as a recognized state code
        """
        try:
            return VIRTUALBOX_ST_TO_STATES[self.machine.state._value][0]
        except KeyError:
            return STATE_UNKNOWN[0]


    #####################
    # tasks
    #####################

    def get_tasks_up(self):
        """ Get the tasks needed for the command "up"
        """
        res = []
        last_task = None

        logger.debug('checking if the virtual machine "%s" exists', self.cfg_name)
        if self.uuid and self.machine:
            logger.debug('... it has UUID: %s [%s]', self.uuid, self.machine)
        else:

            if not self.cfg_name:
                raise MalformedTopologyException('missing attribute in topology: the virtual machine has no "name"')

            try:
                self._box_name = self.cfg_box['name']
            except AttributeError:
                raise MalformedTopologyException('missing attribute in topology: there is no box definition')
            except IndexError:
                raise MalformedTopologyException('missing attribute in topology: box has no name')

            try:
                self._box_url = self.cfg_box['url']
            except IndexError:
                self._box_url = None

            logger.debug('... "%s" does not exist:', self.cfg_name)
            logger.debug('...... will import it from virtualbox template "%s"', self._box_name)
            boxes = boxes_storage_factory()
            self._box_instance = boxes.get_box(name=self._box_name, url=self._box_url)
            if self._box_instance.missing:
                logger.debug('... box "%s" must be downloaded first', self._box_name)
                res += [(self._box_instance.do_download, last_task)]
                last_task = self._box_instance.do_download

            res += [(self.do_copy_appliance, last_task)]
            last_task = self.do_copy_appliance

        res += [(self.do_power_up, last_task)]
        last_task = self.do_power_up

        return res

    def get_tasks_down(self):
        """ Get the tasks needed for the command "down"
        """
        res = []
        last_task = None

        if self.is_running:
            res += [(self.do_power_down, last_task)]
            last_task = self.do_power_down

        return res

    def do_copy_appliance(self):
        """ Copy the appliance as a new virtual machine.
        """
        try:
            self._appliance = self._box_instance.get_appliance('virtualbox')
        except KeyError:
            raise MissingBoxException('box %s does not have a VirtualBox appliance' % (self.cfg_name))
        self._appliance.copy_to_virtualbox(self)

    def do_power_up(self):
        """ Power up the machine via launch
        """
        timeout = getattr(self, 'default_power_up_timeout', _DEFAULT_POWER_UP_TIMEOUT)

        logger.info('powering up "%s"', self.cfg_name)
        s = _virtualbox.Session()
        p = self.machine.launch_vm_process(s, "headless", "")
        p.wait_for_completion(timeout)
        s.unlock_machine()

    def do_power_down(self):
        """ Power down the machine via launch
        """
        timeout = getattr(self, 'default_power_down_timeout', _DEFAULT_POWER_DOWN_TIMEOUT)

        logger.info('powering down "%s"', self.cfg_name)
        session = self.machine.create_session()
        session.console.power_down()
        while self.machine.state >= _virtualbox.library.MachineState.running:
            logger.info('... waiting')
            sleep(1)

    #####################
    # tasks
    #####################
    def __repr__(self):
        """ The representation
        """
        return "<VirtualboxMachine uuid:%s at 0x%x>" % (self.uuid, id(self))

