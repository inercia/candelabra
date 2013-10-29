#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Commands must define, in the __init__ file:
- a DESCRIPTION
- a argparser() function
- a run() function
"""

import sys
import logging
from candelabra.errors import TopologyException, ProviderNotFoundException, CandelabraException

from candelabra.constants import DEFAULT_COMMANDS
from candelabra.loader import load_argparser_for_command, load_runner_for_command
from candelabra.topology.root import TopologyRoot
from candelabra.config import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


_DESCRIPTION = """
The Candelabra VM manager
"""


def main():
    import argparse

    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument('-c',
                        '--config',
                        metavar='FILE',
                        dest='config',
                        type=basestring,
                        default=None,
                        help='configuration file')

    subparsers = parser.add_subparsers(help='commands help', dest='command')

    # for all possible sub-commands, check if they have their own sub-parser and and it if present...
    for command in DEFAULT_COMMANDS:
        parser_module = load_argparser_for_command(command)
        if parser_module:
            try:
                parser_command = subparsers.add_parser(command, help=parser_module.COMMAND_DESCRIPTION)
                parser_module.argparser(parser_command)
            except AttributeError, e:
                logger.warning('command "%s" cannot parse args', command)
            except Exception, e:
                logger.warning('could not load parser for "%s"', command)

    args = parser.parse_args()

    config.load(args.config)

    if hasattr(args, 'topology'):
        # load the topology file and create a tree
        try:
            topology = TopologyRoot()
            topology.load(args.topology)
        except TopologyException, e:
            logger.critical(str(e))
            sys.exit(1)
        except ProviderNotFoundException, e:
            logger.critical(str(e))
            sys.exit(1)
    else:
        topology = None

    # load the runner and run the command with the tree
    runner_module = load_runner_for_command(args.command)
    if not runner_module:
        logger.critical('could not load runner class for command "%s": %s', args.command, str(e))
    else:
        try:
            runner_module.run(args=args, topology=topology, command=args.command)
        except AttributeError, e:
            logger.warning('command "%s" cannot be run: %s', args.command, str(e))
        except CandelabraException, e:
            logger.critical('error: %s', str(e))
            sys.exit(1)

