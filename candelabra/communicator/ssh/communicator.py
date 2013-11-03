#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A SSH communicator plugin
"""

from fabric.api import env, run, sudo

from candelabra.base import Communicator

#: default ssh port
DEFAULT_SSH_PORT = 22


class SshCommunicator(Communicator):
    """ A communicator that communicates with a remote machine
    """

    def __init__(self, machine, credentials):
        """ Initialize a communicator with a remote machine
        :param machine: a hostname or IP address, or a tuple with `(hostname/IP, port)`
        :param credentials: a pair of `(username, password)`
        """
        super(SshCommunicator, self).__init__(machine, credentials)
        self.machine = (machine, DEFAULT_SSH_PORT) if not isinstance(machine, tuple) else machine
        self.credentials = credentials

    def run(self, command):
        env.host_string = "%s:%s" % self.machine
        run(command)

    def sudo(self, command):
        env.host_string = "%s:%s" % self.machine
        sudo(command)

