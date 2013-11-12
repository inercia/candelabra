#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import ProviderPlugin

from .appliance import VirtualboxAppliance
from .machine import VirtualboxMachineNode
from .interface import VirtualboxInterfaceNode
from .network import VirtualboxNetworkNode
from .shared import VirtualboxSharedNode

logger = getLogger(__name__)


class VirtualboxProviderPlugin(ProviderPlugin):
    """ A provider
    """
    NAME = 'virtualbox'
    DESCRIPTION = 'a virtualbox provider'

    # the classes this plugin provides
    APPLIANCE = VirtualboxAppliance
    MACHINE = VirtualboxMachineNode
    NETWORK = VirtualboxNetworkNode
    INTERFACE = VirtualboxInterfaceNode
    SHARED = VirtualboxSharedNode
    COMMUNICATORS = None


provider_instance = VirtualboxProviderPlugin()


def register(registry_instance):
    registry_instance.register(provider_instance.NAME, provider_instance)

