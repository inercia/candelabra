#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import CommandPlugin
from candelabra.errors import UnsupportedCommandException

logger = getLogger(__name__)


class NetCommandPlugin(CommandPlugin):
    NAME = 'net'
    DESCRIPTION = "networking configuration, status, etc..."

    def argparser(self, parser):
        """ Parse arguments
        """
        subparsers = parser.add_subparsers(help='sub-commands available for networking',
                                           dest='net_command')

        # up
        parser_up = subparsers.add_parser('up',
                                          help='setup the network')
        parser_up.add_argument('-t',
                               '--topology',
                               metavar='TOPOLOGY',
                               dest='topology',
                               type=str,
                               default=None,
                               help='the machine(s) definition(s) file(s)')
        parser_up.add_argument('-v',
                               '--verbose',
                               action='store_true',
                               help='verbose display')

        # status
        parser_status = subparsers.add_parser('status',
                                              help='show the networks statuses')
        parser_status.add_argument('-t',
                                   '--topology',
                                   metavar='TOPOLOGY',
                                   dest='topology',
                                   type=str,
                                   default=None,
                                   help='the machine(s) definition(s) file(s)')
        parser_status.add_argument('-v',
                                   '--verbose',
                                   action='store_true',
                                   help='verbose display')

    def run(self, args, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

        if args.net_command == 'up':
            self.run_with_topology(args, args.topology, command='net_up')
        elif args.net_command == 'status':
            self.run_with_topology(args, args.topology, command='net_status')
        else:
            raise UnsupportedCommandException('unknown subcommand "%s"' % args.net_command)


command = NetCommandPlugin()

