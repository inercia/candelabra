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
from candelabra.errors import TopologyException

from candelabra.loader import load_argparser_for_command, load_runner_for_command
from candelabra.topology.root import TopologyRoot


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


_DESCRIPTION = """
The Candelabra VM manager
"""

_COMMANDS = ['up', 'provision']


def main():
    import argparse

    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument('-c',
                        '--config',
                        metavar='FILE',
                        type=basestring,
                        help='configuration file')
    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='the machine(s) definition(s) file(s)')

    subparsers = parser.add_subparsers(help='commands help',
                                       dest='command')

    # for all possible sub-commands, check if they have thei own sub-parser and and it if present...
    for command in _COMMANDS:
        parser_module = load_argparser_for_command(command)
        if parser_module:
            try:
                parser_command = subparsers.add_parser(command, help=parser_module.COMMAND_DESCRIPTION)
                parser_module.argparser(parser_command)
            except AttributeError, e:
                logger.warning('command "%s" cannot parse args', command)

    args = parser.parse_args()

    # load the topology file and create a tree
    try:
        topology = TopologyRoot()
        topology.load(args.infile)
    except TopologyException, e:
        logger.critical(str(e))
        sys.exit(1)

    # load the runner and run the command with the tree
    runner_module = load_runner_for_command(args.command)
    if not runner_module:
        logger.critical('could not load runner class for command "%s": %s', args.command, str(e))
    else:
        try:
            runner_module.run(args)
        except AttributeError, e:
            logger.warning('command "%s" cannot be run: %s', args.command, str(e))

