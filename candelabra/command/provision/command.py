#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import argparse
from logging import getLogger
import sys

from candelabra.base import CommandPlugin

logger = getLogger(__name__)


class ProvisionCommandPlugin(CommandPlugin):
    NAME = 'provision'
    DESCRIPTION = "provision all virtual machines."

    def argparser(self, parser):
        """ Parse arguments
        """
        parser.add_argument('-t',
                            '--topology',
                            metavar='TOPOLOGY',
                            dest='topology',
                            type=argparse.FileType('r'),
                            default=sys.stdin,
                            help='the machine(s) definition(s) file(s)')
        parser.add_argument('--timeout',
                            type=int,
                            help='timeout for the provision')

    def run(self, args, command):
        """ Run the command
        """
        self.run_with_topology(args, args.topology, command)


command = ProvisionCommandPlugin()
