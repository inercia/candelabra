#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import ProviderPlugin

from .appliance import VirtualboxAppliance
from .machine import VirtualboxMachine

logger = getLogger(__name__)


class VirtualboxProviderPlugin(ProviderPlugin):
    """ A provider
    """
    NAME = 'virtualbox'
    DESCRIPTION = 'a virtualbox provider'

    APPLIANCE = VirtualboxAppliance
    MACHINE = VirtualboxMachine


provider_instance = VirtualboxProviderPlugin()


def register(registry_instance):
    registry_instance.register(provider_instance.NAME, provider_instance)

