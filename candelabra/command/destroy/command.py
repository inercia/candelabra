#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import CommandPlugin

logger = getLogger(__name__)


class DestroyCommandPlugin(CommandPlugin):
    NAME = 'destroy'
    DESCRIPTION = "destroys all the machines, freeing all resources like virtual disks, etc..."

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


command = DestroyCommandPlugin()
