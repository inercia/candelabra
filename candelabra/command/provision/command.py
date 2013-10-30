#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import argparse
from logging import getLogger
import sys

from candelabra.base import Command
from candelabra.errors import TopologyException, ProviderNotFoundException
from candelabra.topology.root import TopologyRoot

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

    def run(self, args, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

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

    #####################
    # tasks
    #####################


command = ProvisionCommand()
