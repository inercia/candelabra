#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A SSH communicator plugin
"""

from candelabra.base import Communicator

#: default ssh port
DEFAULT_SSH_PORT = 22


class SshCommunicator(Communicator):
    """ A communicator that communicates with a remote machine
    """

    def __init__(self, machine, **kwargs):
        """ Initialize a communicator with a remote machine
        :param machine: a :class:`MachineNode`
        :param credentials: a pair of `(username, password)`
        """
        super(SshCommunicator, self).__init__(machine)
        from candelabra.topology.machine import MachineNode
        assert isinstance(machine, MachineNode)

    def run(self, command, environment=None):
        from fabric.api import env, run
        env.host_string = "%s:%s" % self.machine
        run(command)

    def sudo(self, command):
        from fabric.api import env, sudo
        env.host_string = "%s:%s" % self.machine
        sudo(command, environment=None)



