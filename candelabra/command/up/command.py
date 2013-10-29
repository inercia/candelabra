import argparse
from logging import getLogger
import sys

from candelabra.base import Command
from candelabra.scheduler.base import Scheduler

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

        scheduler = Scheduler()
        tasks = topology.get_tasks('up')
        scheduler.append(tasks)
        scheduler.run()

    #####################
    # tasks
    #####################


command = UpCommand()
