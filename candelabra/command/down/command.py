#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Command

logger = getLogger(__name__)


class DownCommand(Command):
    DESCRIPTION = "stops all the machines specified in the topology file."

    def argparser(self, parser):
        """ Parse arguments
        """
        parser.add_argument('-t',
                            '--topology',
                            metavar='TOPOLOGY',
                            dest='topology',
                            type=str,
                            default=None,
                            help='the machine(s) definition(s) file(s)')
        parser.add_argument('--timeout',
                            type=int,
                            help='timeout for stopping')

    def run(self, args, command):
        """ Run the command
        """
        self.run_with_topology(args, args.topology, command)


command = DownCommand()
