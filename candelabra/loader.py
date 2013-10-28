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


def load_argparser_for_command(command):
    """ Load a argparser module for a command
    """
    parser_class = '.'.join(COMMANDS_BASE + [command])
    try:
        parser_module = importlib.import_module(parser_class)
    except ImportError:
        return None
    else:
        return parser_module


def load_runner_for_command(command):
    """ Load a runner module for a command
    """
    try:
        runner_class = '.'.join(COMMANDS_BASE + [command])
        runner_module = importlib.import_module(runner_class)
    except ImportError:
        return None
    else:
        return runner_module


def load_machine_for_class(mclass):
    """ Load a machine for a class
    """
    try:
        machine_package = '.'.join(PROVIDER_BASE + [mclass])
        machine_module = importlib.import_module(machine_package)
    except ImportError:
        return None
    else:
        try:
            return machine_module.MACHINE_CLASS
        except AttributeError, e:
            raise MachineDefinitionException('could not find a machine class in "%s"' % machine_module)
