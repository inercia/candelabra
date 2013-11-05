#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A Virtualbox communicator plugin
"""

from logging import getLogger

import virtualbox as _virtualbox

from candelabra.base import Communicator
from candelabra.errors import CommunicatorNotConnectedException


logger = getLogger(__name__)

READ_BUFFER = 100000

class VirtualboxCommunicator(Communicator):
    """ A communicator that communicates with a Virtualbox machine
    """

    def __init__(self, machine, **kwargs):
        """ Initialize a communicator with a remote machine
        :param machine: a :class:`VirtualboxMachineNode` instance
        """
        super(VirtualboxCommunicator, self).__init__(machine)

        from candelabra.provider.virtualbox import VirtualboxMachineNode

        assert isinstance(self.machine, VirtualboxMachineNode)

    def run(self, command, environment=None):
        """ Runs a command on the virtual machine
        """
        if not self.connected:
            raise CommunicatorNotConnectedException('communicator is not connected')

        assert not isinstance(command, basestring)
        assert isinstance(command, list)

        # get a session, lock the machine and run the command
        s = self.machine.lock()
        guest_session = self.machine.get_guest_session(s)

        code = None
        stdout = ''
        stderr = ''
        try:
            environment = [] if not environment else environment
            logger.debug('running "%s"', ' '.join(command))
            guest_process = guest_session.process_create(command[0], command[1:], environment,
                                                         [_virtualbox.library.ProcessCreateFlag.wait_for_std_out],
                                                         timeout_ms=self.machine.cfg_commands_timeout * 1000)
            guest_process.wait_for(_virtualbox.library.ProcessWaitForFlag.terminate._value,
                                   self.machine.cfg_commands_timeout * 1000)

            logger.debug('... pid=%d exit_code=%d', guest_process.pid, guest_process.exit_code)
            code = guest_process.exit_code

            stdout = guest_process.read(0, READ_BUFFER, 1 * 1000)
            stderr = guest_process.read(1, READ_BUFFER, 1 * 1000)

        except _virtualbox.library.VBoxErrorIprtError, e:
            logger.warning(str(e))
        finally:
            #guest_session.close()
            self.machine.unlock(s)

        return code, stdout, stderr

    def write_file(self, content, filename):
        TEMP_FILE = '/tmp/candelabra_upload'
        self.run(['/bin/touch', TEMP_FILE])
        for line in content.splitlines():
            self.run(['/bin/sh', '-c', '\"echo \'%s\' >> %s\"' % (line, TEMP_FILE)])
        self.sudo(['mv', '-f', TEMP_FILE, filename])
