#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Base module for some abstract classes.
"""

from logging import getLogger

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

    def __init__(self, machine, credentials):
        """ Initialize a communication chanel to a :param:`machine` with some :param:`credentials`
        """
        pass

    def run(self, command):
        pass

    def sudo(self, command):
        pass

