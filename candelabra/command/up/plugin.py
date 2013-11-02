#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from command import command as command_instance


def register(registry_instance):
    registry_instance.register(command_instance.NAME, command_instance)

