#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Command

logger = getLogger(__name__)


class UpCommand(Command):
    DESCRIPTION = "creates machines from the box, according to the topology file."

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
                            help='timeout for the provision')

    def run(self, args, command):
        """ Run the command
        """
        self.run_with_topology(args, args.topology, command)


command = UpCommand()
