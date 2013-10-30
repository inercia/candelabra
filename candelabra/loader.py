#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import importlib
from logging import getLogger

from candelabra.errors import MachineDefinitionException
from candelabra.constants import COMMANDS_BASE, PROVIDER_BASE

logger = getLogger(__name__)


def load_command_for(name):
    """ Load a command class for a command
    """
    try:
        command_package = '.'.join(COMMANDS_BASE + [name])
        command_module = importlib.import_module(command_package)
    except ImportError:
        return None
    else:
        try:
            return command_module.COMMAND_INSTANCE
        except AttributeError:
            return None


def load_provider_module_for(name):
    """ Load a box for a provider
    :param name: a provider name (ie, virtualbox)
    :returns: a Box class
    """
    provider_package = '.'.join(PROVIDER_BASE + [name])
    try:
        return importlib.import_module(provider_package)
    except ImportError:
        logger.debug('provider package "%s" not found', provider_package)
        return None


def load_provider_box_for(name):
    """ Load a box for a provider
    :param name: a provider name (ie, virtualbox)
    :returns: a Box class
    """
    provider_module = load_provider_module_for(name)
    if provider_module:
        try:
            return provider_module.BOX_CLASS
        except AttributeError, e:
            raise MachineDefinitionException('could not find a box class in "%s"' % provider_module)


def load_provider_machine_for(name):
    """ Load a provider machine for a name
    :param name: a provider name (ie, virtualbox)
    """
    provider_module = load_provider_module_for(name)
    if provider_module:
        try:
            return provider_module.MACHINE_CLASS
        except AttributeError, e:
            raise MachineDefinitionException('could not find a machine class in "%s"' % provider_module)
