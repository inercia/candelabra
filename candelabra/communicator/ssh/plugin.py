#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import CommunicatorPlugin

from .communicator import SshCommunicator

logger = getLogger(__name__)


class SshCommunicatorPlugin(CommunicatorPlugin):
    """ A communicator
    """
    NAME = 'ssh'
    DESCRIPTION = 'a ssh communicator'
    COMMUNICATOR = SshCommunicator

communicator_instance = SshCommunicatorPlugin()


def register(registry_instance):
    registry_instance.register(communicator_instance.NAME, communicator_instance)

