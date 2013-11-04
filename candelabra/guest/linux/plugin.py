#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import GuestPlugin

from .guest import LinuxGuest

logger = getLogger(__name__)


class LinuxGuestPlugin(GuestPlugin):
    """ A Linux guest definition
    """
    NAME = 'linux'
    DESCRIPTION = 'a Linux guest'
    GUEST = LinuxGuest

guest_instance = LinuxGuestPlugin()


def register(registry_instance):
    registry_instance.register(guest_instance.NAME, guest_instance)


