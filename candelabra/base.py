#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Base module for some abstract classes.
"""

from logging import getLogger
from weakref import proxy

logger = getLogger(__name__)


class Provisioner(object):
    """ A provisioner

    Provisioners are responsible for performing actions on the machines once these machines are up
    and running. These actions are usually software installation, file contents setting, etc...
    """
    pass


class Communicator(object):
    """ A communicator

    Communicators are communication channels with the machines. A typical communicator is 'ssh'.
    """

    def __init__(self, machine, **kwargs):
        """ Initialize a communication chanel to a :param:`machine` of class :class:`MachineNode`
        """
        from candelabra.topology.machine import MachineNode

        assert isinstance(machine, MachineNode)
        self.machine = proxy(machine)
        self.connected = False

    def run(self, command, environment=None, verbose=False):
        pass

    def sudo(self, command, environment=None, verbose=False):
        """ Runs a command in the virtual machine with sudo
        """
        assert not isinstance(command, basestring)
        assert isinstance(command, list)

        sudo_command = self.machine.cfg_box.cfg_sudo_command
        real_command = '%s' % ' '.join(command)
        if len(real_command) > 0:
            return self.run([sudo_command, 'sh', '-c', real_command])
        else:
            return None, None, None

    def sudo_lines(self, commands_string, environment=None, verbose=False, **kwargs):
        """ Run a a list of lines, provided as a long string
        """
        for line in commands_string.splitlines():
            if line:
                line_exp = line.format(**kwargs).strip()
                code, stdout, stderr = self.machine.communicator.sudo(line_exp.split(' '))
                if code > 0:
                    for l in stderr.splitlines():
                        logger.debug('stderr: %s', l)

    def test(self, condition):
        return bool(int(self.run('[ -e {condition} ] && echo 1 || echo 0'.format(condition=condition))))


class Guest(object):
    """ A guest
    """

    def __init__(self, machine, communicator=None, **kwargs):
        from candelabra.topology.machine import MachineNode

        assert isinstance(machine, MachineNode)
        assert isinstance(communicator, Communicator)
        self.machine = proxy(machine)
        self.communicator = proxy(communicator) if communicator else proxy(machine.communicator)

    def mount(self, directory, mount_point):
        """ Mount a directory on a mount point
        """
        raise NotImplementedError()

    def mkdir(self, directory):
        """ Create a remote directory
        """
        raise NotImplementedError()

    def shutdown(self):
        """ Shutdown the machine
        """
        raise NotImplementedError()

    def get_ips(self):
        """ Get the IP addresses
        """
        raise NotImplementedError()

    def change_hostname(self, name):
        """ Set the current hostname
        """
        raise NotImplementedError()

    def setup_iface(self, number, type, ip='', netmask=''):
        """ Setup a network interface
        """
        raise NotImplementedError()
