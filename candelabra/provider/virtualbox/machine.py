#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import shutil
from time import sleep

import virtualbox as _virtualbox

from candelabra.config import config
from candelabra.constants import DEFAULT_CFG_SECTION_VIRTUALBOX, CFG_USERLAND_TIMEOUT, CFG_MACHINE_UPDOWN_TIMEOUT, CFG_MACHINE_COMMANDS_TIMEOUT
from candelabra.errors import MachineChangeException, MachineException, MalformedTopologyException
from candelabra.plugins import build_communicator_instance, build_guest_instance
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

LOCK_TYPES = {
    'shared': _virtualbox.library.LockType.shared,
    'write': _virtualbox.library.LockType.write,
}


########################################################################################################################


class VirtualboxMachineNode(MachineNode):
    """ A VirtualBox machine
    """

    # known attributes
    # the right tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = [
        TopologyAttribute('path', str, default=''),
        TopologyAttribute('updown_timeout', int, default=None),
        TopologyAttribute('gui', str, default='headless'),
        TopologyAttribute('username', str, default='vagrant'),
        TopologyAttribute('password', str, default='vagrant'),
        TopologyAttribute('userland_timeout', int, default=None),
        TopologyAttribute('commands_timeout', int, default=None),
    ]

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
        self._vbox_uuid = self.cfg_uuid if getattr(self, 'cfg_uuid', None) else None
        self._vbox_machine = None
        self._vbox_guest = None
        self._vbox_guest_os_type = None
        self._vbox_wait_events = {}

        self._created_shared_folders = []

        # check and fix topology parameters
        if not self.cfg_gui in ['headless', 'gui']:
            raise MalformedTopologyException('invalid GUI type %s', self.cfg_gui)
        if not self.cfg_updown_timeout:
            self.cfg_updown_timeout = config.get_key(CFG_MACHINE_UPDOWN_TIMEOUT)
        if not self.cfg_userland_timeout:
            self.cfg_userland_timeout = config.get_key(CFG_USERLAND_TIMEOUT)
        if not self.cfg_commands_timeout:
            self.cfg_commands_timeout = config.get_key(CFG_MACHINE_COMMANDS_TIMEOUT)

        # create a communicator for this machine
        self.communicator = build_communicator_instance(_class='virtualbox', machine=self)

    def sync_name(self):
        """ Set the VirtualBox virtual machine name to the same name as this node
        """
        assert not self.is_global

        logger.debug('synchronizing VM name: setting as %s', self.cfg_name)
        try:
            s = self.lock(lock_type='write')
            new_machine = s.machine
            new_machine.name = self.cfg_name
            new_machine.save_settings()
            self.unlock(s)
        except _virtualbox.library.VBoxError, e:
            raise MachineChangeException(str(e))
        else:
            sleep(1.0)

    def check_name(self):
        """ Check that the configured name matches the real VM name
        """
        assert not self.is_global

        if self._vbox_machine.name != self.cfg_name:
            logger.warning('the configured name (%s) does not match the VM name (%s)',
                           self.cfg_name, self._vbox_machine.name)
            return False
        return True

    #####################
    # properties
    #####################

    def get_uuid(self):
        """ Get the machine UUID
        """
        return self._vbox_uuid

    def set_uuid(self, val):
        """ Set the machine UUID
        """
        self._vbox_uuid = val
        self._vbox_machine = None

    cfg_uuid = property(get_uuid, set_uuid)

    def get_vbox_machine(self):
        """ Get the underlying VirtualBox "machine" instance
        """
        try:
            if self._vbox_uuid and not self._vbox_machine:
                logger.debug('(getting machine for %s [UUID:%s])', self.cfg_name, self._vbox_uuid)
                self._vbox_machine = self._vbox.find_machine(self._vbox_uuid)
        except _virtualbox.library.VBoxErrorObjectNotFound, e:
            logger.debug(str(e))
        return self._vbox_machine

    vbox_machine = property(get_vbox_machine)

    def get_info(self):
        """ Get some machine information
        """
        return 'name: %s UUID:%s ' % (self.cfg_name, self.cfg_uuid) + \
               'CPUs:%d (exec-cap:%d) ' % (self.vbox_machine.cpu_count, self.vbox_machine.cpu_execution_cap) + \
               'mem:%d vram:%d ' % (self.vbox_machine.memory_size, self.vbox_machine.vram_size) + \
               'state:%s ' % (str(self.vbox_machine.state))

    def get_guest_type(self, locked_session=None):
        """ Get the guess type, as a tuple of (name, description)
        """
        res = (None, None)
        try:
            s = locked_session if locked_session else self.lock()
            t = self._vbox.get_guest_os_type(s.machine.os_type_id)
            res = (t.family_id.lower(), t.family_description)
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        finally:
            if not locked_session:
                self.unlock(s)

        return res

    def get_guest_level_system(self, guest=None, session=None):
        """ Return True if the guest session level is system
        """
        if not guest:
            s = self.lock() if not session else session
            guest = s.console.guest

        res = bool(guest.get_additions_status(_virtualbox.library.AdditionsRunLevelType.system))
        if not guest and not session:
            self.unlock(s)
        return res

    def get_guest_level_userland(self, guest=None, session=None):
        """ Return True if the guest session level is userland
        """
        if not guest:
            s = self.lock() if not session else session
            guest = s.console.guest

        res = bool(guest.get_additions_status(_virtualbox.library.AdditionsRunLevelType.userland))
        if not session:
            self.unlock(s)
        return res

    def get_state(self):
        """ Get the VirtualBox machine state, as a recognized state code
        """
        if self.vbox_machine:
            try:
                return _VIRTUALBOX_ST_TO_STATES[self.vbox_machine.state._value][0]
            except AttributeError, e:
                logger.debug('no machine state available: %s', str(e))
            except KeyError, e:
                logger.debug('no machine state available: %s', str(e))

        return STATE_UNKNOWN[0]

    def wait_for_event(self, event, timeout=10000):
        """ Wait for an event
        :param event: an instance of _virtualbox.library.VBoxEventType
        """
        self._vbox_wait_events[event] = False

        def on_property_change(_event):
            logger.debug('event: %s %s %s', _event.name, _event.value, _event.flags)
            self._vbox_wait_events[event] = True

        callback_id = self._vbox.event_source.register_callback(on_property_change, event)

        # wait for some time...
        num = 0
        while not self._vbox_wait_events[event]:
            sleep(1.0)
            num += 1
            if num >= timeout:
                break

        # clenaup
        del self._vbox_wait_events[event]
        _virtualbox.events.unregister_callback(callback_id)

    #####################
    # guest sessions
    #####################

    def get_guest_session(self, session, username='vagrant', password='vagrant', name='vagrant'):
        """ Get or create a guest session
        """
        guest_sessions = session.console.guest.sessions
        if len(guest_sessions) == 0:
            guest_session = session.console.guest.create_session(username, password, '', name)
            guest_session.wait_for_array([_virtualbox.library.GuestSessionWaitForFlag.start],
                                         timeout_ms=self.cfg_updown_timeout * 1000)
        else:
            guest_session = guest_sessions[0]
        return guest_session

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

    def listen_events(self):
        """ Listen for events
        """

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

    #####################
    # locking
    #####################

    def lock(self, session=None, lock_type='shared'):
        """ Lock the machine
        """
        assert lock_type in ['shared', 'write']
        assert self._vbox_machine is not None
        session = session if session else _virtualbox.Session()
        self.vbox_machine.lock_machine(session, LOCK_TYPES[lock_type])
        return session

    def unlock(self, session):
        """ Unlock the machine
        """
        session.unlock_machine()

    #####################
    # scheduling
    #####################

    def get_tasks_net_bridge(self):
        """ Get the tasks needed for the command "net up"
        """
        if self.is_running:
            logger.info('machine %s seems to be running', self.cfg_name)
            self.add_task_seq(self.do_wait_userland)
            self.add_task_seq(self.do_bridge)
        else:
            logger.error('machine %s is not running!', self.cfg_name)
            logger.error('... it must be running for this command (it will not be started automatically)')

    #####################
    # tasks
    #####################

    def do_power_up(self):
        """ Power up the machine via launch
        """
        self.listen_events()

        logger.info('powering up "%s"', self.cfg_name)
        try:
            s = _virtualbox.Session()
            p = self.vbox_machine.launch_vm_process(s, self.cfg_gui, "")
            logger.info('... waiting from completion (up to %d seconds)', self.cfg_updown_timeout)
            p.wait_for_completion(self.cfg_updown_timeout * 1000)
            self.unlock(s)
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)

    def do_wait_userland(self):
        """ Wait for the guest session to be in userland-ready

        Once the session is in userland-ready, we can launch processes from here...
        """
        logger.info('waiting for userland on "%s"', self.cfg_name)
        s = self.lock()
        try:
            logger.debug('getting guest information...')
            self._vbox_guest = s.console.guest
            self._vbox_guest_os_type = self._vbox.get_guest_os_type(s.machine.os_type_id)

            logger.info('... guest OS: %s (%s)' % self.get_guest_type(locked_session=s))

            logger.debug('... guest additions: vers:%s - rev:%s ',
                         self._vbox_guest.additions_version,
                         self._vbox_guest.additions_revision)

            logger.info('waiting for machine up to %d seconds...', self.cfg_userland_timeout)
            for _ in xrange(self.cfg_userland_timeout):
                systemland = self.get_guest_level_system(guest=self._vbox_guest, session=s)
                userland = self.get_guest_level_userland(guest=self._vbox_guest, session=s)
                logger.debug('... status: system=%s userland=%s', systemland, userland)
                if userland and systemland:
                    break
                else:
                    sleep(1.0)

            logger.debug('%s facilities:', self.cfg_name)
            for f in self._vbox_guest.facilities:
                logger.debug('... %s', f.name)

        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)
            self.communicator.connected = True
        finally:
            self.unlock(s)

    def do_create_guest(self):
        """ Create a guest reference, creating a :class:`Guest` instance that can be used for
        mounting directories, creating network devices, etc...
        """
        logger.debug('creating guest reference...')
        guest_type, guest_descr = self.get_guest_type()
        self.guest = build_guest_instance(_class=guest_type, machine=self, communicator=self.communicator)

    def do_power_down(self):
        """ Power down the machine
        """
        s = self.lock()
        try:
            #if self.guest:
            #    self.guest.shutdown()
            # # wait for a change in the machine state

            p = s.console.power_down()
            logger.info('... waiting from power down to finish (up to %d seconds)', self.cfg_updown_timeout)
            p.wait_for_completion(self.cfg_updown_timeout * 1000)
            logger.debug('...... done [code:%d]', p.result_code)
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)
            self.communicator.connected = False
        finally:
            self.unlock(s)
            self._vbox_guest = None
            self._vbox_guest_os_type = None

    def do_pause(self):
        """ Pause the machine via launch
        """
        logger.info('powering down "%s"', self.cfg_name)
        s = self.lock()
        try:
            p = s.console.pause()
            logger.info('... waiting from power down to finish (up to %d seconds)', self.cfg_updown_timeout)
            while self.vbox_machine.state >= _virtualbox.library.MachineState.running:
                sleep(1.0)
                # p.wait_for_completion(self.cfg_updown_timeout * 1000)
            logger.debug('...... done [code:%d]', p.result_code)
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        else:
            sleep(1.0)
            self.communicator.connected = False
        finally:
            self.unlock(s)

    def do_copy_appliance(self):
        """ Copy the appliance as a new virtual machine.
        """
        logger.debug('copying the appliance...')
        super(VirtualboxMachineNode, self).do_copy_appliance()

        # we must synchronize the name, as the appliance can be something like 'redhat-minimal' and
        # we want to set a nice, friendly name...
        self.sync_name()

    def do_destroy(self):
        """ Destroy a virtual machine
        """
        sleep(1.0)
        logger.info('destroying %s', self.cfg_name)
        try:
            if self.vbox_machine:
                media = self.vbox_machine.unregister(_virtualbox.library.CleanupMode.full)
                p = self.vbox_machine.delete_config(media)
                p.wait_for_completion(-1)
                self.vbox_machine.save_settings()
        except _virtualbox.library.VBoxErrorIprtError, e:
            logger.warning(str(e))
        else:
            sleep(1.0)
            properties = self._vbox.system_properties
            full_path = os.path.join(properties.default_machine_folder, self.cfg_name)
            if os.path.isdir(full_path):
                logger.debug('... removing %s', full_path)
                shutil.rmtree(full_path)

        self.communicator.connected = False
        self._vbox_uuid = None
        self._vbox_machine = None
        self._vbox_guest = None
        self._vbox_guest_os_type = None

    def do_create_guest_reference(self):
        """ Create a communicator for this machine
        """
        t, desc = self.get_guest_type()
        logger.debug('creating a %s guest reference', t)
        self.guest = build_guest_instance(_class=t, machine=self)

    def do_create_user(self):
        """ Create a user
        """
        logger.info('creating user/pass=%s/%s in "%s"', self.cfg_username, self.cfg_password, self.cfg_name)
        s = self.lock()
        try:
            s.console.guest.set_credentials(self.cfg_username, self.cfg_password, '', False)
        except _virtualbox.library.VBoxError, e:
            raise MachineException(str(e))
        finally:
            self.unlock(s)

    def do_bridge(self):
        """ Create a port bridge
        """
        # get a session, lock the machine and run the command
        #s = self.lock()
        #guest_session = self.get_guest_session(s)
        #LISTEN_ADDR = ('0.0.0.0', 2222)
        #
        # import socket
        # try:
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #
        #     logger.info('Binding to %s', str(LISTEN_ADDR))
        #     sock.bind(LISTEN_ADDR)
        #     sock.listen(1)
        # except socket.error, e:
        #     logger.warning('socket error: %s', str(e))
        #     return
        #
        # conn, addr = sock.accept()
        # logger.info('Connected from %s', str(addr))
        #
        # try:
        #     command = ["/usr/bin/nc", "127.0.0.1", "22"]
        #     logger.debug('running "%s"', ' '.join(command))
        #     guest_process = guest_session.process_create(command[0], command[1:], [],
        #                                                  [_virtualbox.library.ProcessCreateFlag.wait_for_std_out],
        #                                                  timeout_ms=10 * 1000)
        #
        #     # wait for the command to start
        #     guest_process.wait_for(_virtualbox.library.ProcessWaitForFlag.start._value,
        #                            10 * 1000)
        #     logger.debug('... pid=%d exit_code=%d', guest_process.pid, guest_process.exit_code)
        #
        #     conn.setblocking(False)
        #     while True:
        #         stdin = conn.recv(10000)
        #         if not stdin:
        #             break
        #         else:
        #             logger.debug('VM <-[ %d bytes ]- host', len(stdin))
        #             guest_process.write(0, 0, stdin, 0)
        #
        #         stdout = guest_process.read(0, 100000, 10)
        #         logger.debug('VM -[ %d bytes ]-> host', len(stdout))
        #         if stdout:
        #             conn.sendall(stdout)

        #except _virtualbox.library.VBoxErrorIprtError, e:
        #    logger.warning(str(e))
        #except KeyboardInterrupt:
        #    logger.info('Interrupted')
        #finally:
        #    #guest_session.close()
        #    self.unlock(s)
        #    #conn.close()
        pass



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
