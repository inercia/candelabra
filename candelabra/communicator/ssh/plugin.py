#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Communicator

logger = getLogger(__name__)


class SshCommunicator(Communicator):
    """ A communicator
    """
    NAME = 'ssh'
    DESCRIPTION = 'a ssh communicator'


communicator_instance = SshCommunicator()


def register(registry_instance):
    registry_instance.register(communicator_instance.NAME, communicator_instance)

