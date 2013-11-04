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

    def run(self, command, environment=None):
        pass

    def sudo(self, command, environment=None):
        pass


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
        pass

