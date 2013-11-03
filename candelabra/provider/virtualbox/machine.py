#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from time import sleep

import virtualbox as _virtualbox

from candelabra.config import config
from candelabra.tasks import TaskGenerator
from candelabra.constants import DEFAULT_CFG_SECTION_VIRTUALBOX
from candelabra.errors import MissingBoxException, MalformedTopologyException, MachineChangeException, MachineException
from candelabra.topology.machine import MachineNode
from candelabra.topology.machine import STATE_POWERDOWN, STATE_RUNNING, STATE_PAUSED, STATE_ABORTED, STATE_STARTING, STATE_STOPPING, STATE_UNKNOWN
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)

# a mapping between VirtualMachine states and Candelabra states
_VIRTUALBOX_ST_TO_STATES = {
    1: STATE_POWERDOWN,
    4: STATE_ABORTED,
    5: STATE_RUNNING,
    6: STATE_PAUSED,
    10: STATE_STARTING,
    11: STATE_STOPPING,
}

########################################################################################################################

_DEFAULT_SESSION_TIMEOUT = 15 * 1000
""" Default timeout for getting a valid session (in milliseconds)
"""

_DEFAULT_POWER_UP_TIMEOUT = 5 * 1000
""" Default timeout while waiting for power up a machine (in milliseconds)
"""

_DEFAULT_POWER_DOWN_TIMEOUT = 5 * 1000
""" Default timeout while waiting for power down a machine (in milliseconds)
"""


########################################################################################################################


class VirtualboxMachineNode(MachineNode):
    """ A VirtualBox machine
    """

    # known attributes
    # the right tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = {
        'path': TopologyAttribute(constructor=str, default='', inherited=True),
    }

    # attributes that are saved in the state file
    _state_attributes = {
        'state',
    }

    def __init__(self, **kwargs):
        """ Initialize a VirtualBox machine
        """
        super(VirtualboxMachineNode, self).__init__(**kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

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
        self._events = {}
        self._guest_session = None
        self._created_shared_folders = []

    def sync_name(self):
        """ Set the VirtualBox virtual machine name to the same name as this node
        """
        logger.debug('synchronizing VM name: setting as %s', self.cfg_name)
        try:
            s = _virtualbox.Session()
            self.machine.lock_machine(s, _virtualbox.library.LockType.write)
            new_machine = s.machine
            new_machine.name = self.cfg_name
            new_machine.save_settings()
            s.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineChangeException(str(e))
        else:
            sleep(1.0)

    def check_name(self):
        """ Check that the configured name matches the real VM name
        """
        if self._machine.name != self.cfg_name:
            logger.warning('the configured name (%s) does not match the VM name (%s)',
                           self.cfg_name, self._machine.name)
            return False
        return True

    #####################
    # properties
    #####################

    def get_uuid(self):
        """ Get the machine UUID
        """
        return self._uuid

    def set_uuid(self, val):
        """ Set the machine UUID
        """
        self._uuid = val
        self._machine = None

    cfg_uuid = property(get_uuid, set_uuid)

    def get_machine(self):
        """ Get the underlying VirtualBox "machine" instance
        """
        try:
            if self._uuid and not self._machine:
                self._machine = self._vbox.find_machine(self._uuid)
        except _virtualbox.library.VBoxErrorObjectNotFound, e:
            logger.debug(str(e))
        return self._machine

    machine = property(get_machine)

    def get_info(self):
        """ Get some machine information
        """
        return 'name: %s UUID:%s ' % (self.cfg_name, self.cfg_uuid) + \
               'CPUs:%d (exec-cap:%d) ' % (self.machine.cpu_count, self.machine.cpu_execution_cap) + \
               'mem:%d vram:%d ' % (self.machine.memory_size, self.machine.vram_size) + \
               'state:%s ' % (str(self.machine.state))

    def get_state(self):
        """ Get the VirtualBox machine state, as a recognized state code
        """
        try:
            return _VIRTUALBOX_ST_TO_STATES[self.machine.state._value][0]
        except AttributeError, e:
            logger.debug('no machine state available: %s', str(e))
            return STATE_UNKNOWN[0]
        except KeyError, e:
            logger.debug('no machine state available: %s', str(e))
            return STATE_UNKNOWN[0]

    def wait_for_event(self, event, timeout=10000):
        """ Wait for an event
        :param event: an instance of _virtualbox.library.VBoxEventType
        """
        self._events[event] = False

        def on_property_change(_event):
            logger.debug('event: %s %s %s', _event.name, _event.value, _event.flags)
            self._events[event] = True

        callback_id = self._vbox.event_source.register_callback(on_property_change, event)

        # wait for some time...
        num = 0
        while not self._events[event]:
            sleep(1.0)
            num += 1
            if num >= timeout:
                break

        # clenaup
        del self._events[event]
        _virtualbox.events.unregister_callback(callback_id)

    def wait_for_session_state_change(self, timeout=5):
        """ Wait for the session state to change
        """
        logger.debug('waiting up to %d seconds for state change...', timeout)
        self.wait_for_event(event=_virtualbox.library.VBoxEventType.on_session_state_changed, timeout=timeout)

    def wait_for_guest_session_state_change(self, timeout=5):
        """ Wait for the session state to change
        """
        logger.debug('waiting up to %d seconds for guest session state change...', timeout)
        self.wait_for_event(event=_virtualbox.library.VBoxEventType.on_guest_session_state_changed, timeout=timeout)


    #####################
    # scheduling
    #####################

    def get_tasks_up(self):
        """ Get the tasks needed for the command "up"
        """
        if not self.cfg_name:
            raise MalformedTopologyException('missing attribute in topology: the virtual machine has no "name"')

        self.clear_tasks()

        logger.debug('checking if the virtual machine "%s" exists', self.cfg_name)
        if self.cfg_uuid and self.machine:
            logger.info('... %s seems to have been already created', self.machine)
        else:
            logger.info('"%s" does not seem to exist', self.cfg_name)
            logger.info('... will import it from VirtualBox appliance "%s"', self.cfg_box.cfg_name)
            if self.cfg_box.missing:
                logger.debug('... box "%s" must be downloaded first', self.cfg_name)
                self.add_task_seq(self._box_instance.do_download)

            self.add_task_seq(self.do_copy_appliance)
            self.add_task_seq(self.do_sync_name)

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

    #####################
    # tasks
    #####################

    def do_power_up(self):
        """ Power up the machine via launch
        """
        timeout = getattr(self, 'default_power_up_timeout', _DEFAULT_POWER_UP_TIMEOUT)

        def on_property_change(_event):
            logger.debug('event: %s', _event)

        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_state_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_session_state_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_machine_state_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_additions_state_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_shared_folder_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_guest_keyboard)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_guest_session_state_changed)
        self._vbox.event_source.register_callback(on_property_change,
                                                  _virtualbox.library.VBoxEventType.on_guest_process_registered)

        logger.info('powering up "%s"', self.cfg_name)
        try:
            s = _virtualbox.Session()
            #p = self.machine.launch_vm_process(s, "headless", "")
            p = self.machine.launch_vm_process(s, "gui", "")
            logger.info('... waiting from completion (up to %d seconds)', timeout / 1000)
            p.wait_for_completion(timeout)
            s.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)

    def do_power_down(self):
        """ Power down the machine via launch
        """
        timeout = getattr(self, 'default_power_down_timeout', _DEFAULT_POWER_DOWN_TIMEOUT)
        logger.info('powering down "%s"', self.cfg_name)

        try:
            s = _virtualbox.Session()
            self.machine.lock_machine(s, _virtualbox.library.LockType.shared)
            p = s.console.power_down()
            logger.info('... waiting from power down to finish (up to %d seconds)', timeout / 1000)
            p.wait_for_completion(timeout)
            logger.debug('...... done [code:%d]', p.result_code)
            s.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)

    def do_pause(self):
        """ Pause the machine via launch
        """
        timeout = getattr(self, 'default_power_down_timeout', _DEFAULT_POWER_DOWN_TIMEOUT)

        logger.info('powering down "%s"', self.cfg_name)
        try:
            s = _virtualbox.Session()
            self.machine.lock_machine(s, _virtualbox.library.LockType.shared)
            p = s.console.pause()
            logger.info('... waiting from power down to finish (up to %d seconds)', timeout / 1000)
            while self.machine.state >= _virtualbox.library.MachineState.running:
                sleep(1.0)
                # p.wait_for_completion(timeout)
            logger.debug('...... done [code:%d]', p.result_code)
            s.unlock_machine()
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))

    def do_copy_appliance(self):
        """ Copy the appliance as a new virtual machine.
        """
        self._appliance = self.cfg_box.get_appliance('virtualbox')
        if not self._appliance:
            raise MissingBoxException('box "%s" does not have a VirtualBox appliance' % self.cfg_box.cfg_name)

        self._appliance.import_to_machine(self)

    def do_sync_name(self):
        """ Synchronize the configured name with the VM name
        """
        self.sync_name()

    def do_create_guest_session(self):
        """ Create a guest session
        """
        timeout = getattr(self, 'default_session_timeout', _DEFAULT_SESSION_TIMEOUT)
        res = 0

        sleep(1.0)
        s = _virtualbox.Session()
        self.machine.lock_machine(s, _virtualbox.library.LockType.shared)
        logger.info('waiting for guest session on %s', self.cfg_name)
        self._guest_session = s.console.guest.create_session('vagrant', 'vagrant')
        try:
            sleep(1.0)
            res = self._guest_session.wait_for_array([_virtualbox.library.GuestSessionWaitForFlag.start],
                                                     timeout_ms=timeout)
            logger.info('... guest session started')
        except _virtualbox.library.VBoxErrorIprtError, e:
            logger.warning(str(e))
            logger.debug(res)
        finally:
            s.unlock_machine()

        sleep(50.0)

    def do_run_echo(self):
        session = self.machine.create_session()
        guest = session.console.guest.create_session('vagrant', 'vagrant')
        try:
            p, o, e = guest.execute('/bin/ls', ['-lisa'], timeout_ms=10 * 1000)
            p.wait_for_array([_virtualbox.library.ProcessWaitForFlag(8),
                              _virtualbox.library.ProcessWaitForFlag(16),
                              _virtualbox.library.ProcessWaitForFlag.terminate], 3 * 1000)

            logger.debug('pid=%d exit_code=%d', p.pid, p.exit_code)
            logger.debug('output="%s"', o)
            for line in o.splitlines():
                logger.debug('output="%s"', line)
            logger.debug('error="%s"', e)
        except _virtualbox.library.VBoxErrorIprtError, e:
            logger.warning(str(e))
        finally:
            guest.close()

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
        if self._parent is None:
            extra += ['global']

        return "<VirtualboxMachine(%s) at 0x%x>" % (','.join(extra), id(self))
