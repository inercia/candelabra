#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Provisioner

logger = getLogger(__name__)


class PuppetProvisioner(Provisioner):
    """ A provisioner
    """
    NAME = 'puppet'
    DESCRIPTION = 'a puppet provisioner'


provisioner_instance = PuppetProvisioner()


def register(registry_instance):
    registry_instance.register(provisioner_instance.NAME, provisioner_instance)

