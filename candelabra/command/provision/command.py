import argparse
from logging import getLogger
import sys

from candelabra.base import Command

logger = getLogger(__name__)


class ProvisionCommand(Command):
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

    def run(self, args, topology, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

    #####################
    # tasks
    #####################

command = ProvisionCommand()
