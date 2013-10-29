import argparse
from logging import getLogger
import sys

from candelabra.base import Command
from candelabra.scheduler.base import Scheduler

logger = getLogger(__name__)


class ShowCommand(Command):
    DESCRIPTION = "show information."

    def argparser(self, parser):
        """ Parse arguments
        """
        subparsers = parser.add_subparsers(help='sub-commands available for showing',
                                           dest='show_command')

        # boxes
        parser_a = subparsers.add_parser('boxes',
                                         help='show the list of boxes')
        parser_a.add_argument('-v',
                              '--verbose',
                              action='store_true',
                              help='verbose display')

        # topologies
        parser_a = subparsers.add_parser('topologies',
                                         help='show the list of created topologies')
        parser_a.add_argument('-v',
                              '--verbose',
                              action='store_true',
                              help='verbose display')

    def run(self, args, topology, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

        scheduler = Scheduler()
        tasks = topology.get_tasks('up')
        scheduler.append(tasks)
        scheduler.run()

    #####################
    # tasks
    #####################


command = ShowCommand()
