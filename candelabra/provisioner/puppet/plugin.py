#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import ProvisionerPlugin

from .provision import PuppetProvisioner

logger = getLogger(__name__)


class PuppetProvisionerPlugin(ProvisionerPlugin):
    """ A provisioner
    """
    NAME = 'puppet'
    DESCRIPTION = 'a puppet provisioner'
    PROVISIONER = PuppetProvisioner

provisioner_instance = PuppetProvisionerPlugin()


def register(registry_instance):
    registry_instance.register(provisioner_instance.NAME, provisioner_instance)


