#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import CommunicatorPlugin

from .communicator import VirtualboxCommunicator

logger = getLogger(__name__)


class VirtualboxCommunicatorPlugin(CommunicatorPlugin):
    """ A Virtualbox communicator
    """
    NAME = 'virtualbox'
    DESCRIPTION = 'a virtualbox communicator'
    COMMUNICATOR = VirtualboxCommunicator

communicator_instance = VirtualboxCommunicatorPlugin()


def register(registry_instance):
    registry_instance.register(communicator_instance.NAME, communicator_instance)

