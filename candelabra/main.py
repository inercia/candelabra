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

from candelabra.errors import CandelabraException
from candelabra.plugins import register_all, PLUGINS_REGISTRIES
from candelabra.config import config
from candelabra import logs

_DESCRIPTION = """
The Candelabra VM manager.
"""

_VERBOSE_TEXT = """
Candelabra can used for:

* downloading Boxes (virtual machines templates) [candelabra import --help]
  example:

   $ candelabra import --url http://some.url.com/centos.box --name centos-6.4

* bringing up topologies with machines [candelabra up --help]
  example:

   $ candelabra up -t topology.yaml
"""


def main():
    import argparse

    parser = argparse.ArgumentParser(description=_DESCRIPTION,
                                     add_help=True)
    parser.add_argument('-c',
                        '--config',
                        metavar='FILE',
                        dest='config',
                        type=basestring,
                        default=None,
                        help='configuration file')

    parser.add_argument('-L',
                        '--log-level',
                        dest='loglevel',
                        default='info',
                        choices=logs.LOGLEVELS + [l.lower() for l in logs.LOGLEVELS],
                        help="console log level")

    parser.add_argument('--log-file',
                        dest='logfile',
                        default=None,
                        help="log file")

    parser.add_argument('--log-file-level',
                        dest='logfilelevel',
                        default=None,
                        choices=logs.LOGLEVELS + [l.lower() for l in logs.LOGLEVELS],
                        help="log file level")

    subparsers = parser.add_subparsers(help='supported commands help:',
                                       dest='command')

    _delayed_warnings = None

    register_all()

    # for all possible sub-commands, check if they have their own sub-parser and and it if present...
    commands = PLUGINS_REGISTRIES['candelabra.command']
    for command_name, command_instance in commands.plugins.iteritems():
        try:
            parser_command = subparsers.add_parser(command_name, help=command_instance.DESCRIPTION)
            command_instance.argparser(parser_command)
        except AttributeError, e:
            _delayed_warnings = 'command "%s" cannot parse args' % command_name
        except Exception, e:
            _delayed_warnings = 'could not load parser for "%s"' % command_name

    args = parser.parse_args()

    logs.setup_console(level=args.loglevel.upper())
    logger = logging.getLogger(__name__)

    if _delayed_warnings:
        logger.warn(_delayed_warnings)

    config.load(args.config)

    logs.setup_file(filename=args.logfile, level=args.logfilelevel.upper() if args.logfilelevel else None)

    # load the runner and run the command with the tree
    command_instance = commands.plugins[args.command]
    try:
        command_instance.run(args=args, command=args.command)
    except CandelabraException, e:
        logger.critical('error: %s', str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
