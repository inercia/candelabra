#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Guest

logger = getLogger(__name__)


class LinuxGuest(Guest):
    """ A Linux guest definition
    """
    NAME = 'linux'
    DESCRIPTION = 'a Linux guest'


guest_instance = LinuxGuest()


def register(registry_instance):
    registry_instance.register(guest_instance.NAME, guest_instance)

