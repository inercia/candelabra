#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import sys

from candelabra.base import Command
from candelabra.errors import TopologyException, ProviderNotFoundException
from candelabra.scheduler.base import Scheduler
from candelabra.topology.root import TopologyRoot

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
        logger.info('running command "%s"', command)

        if args.topology is None:
            logger.critical('no topology file provided')
            sys.exit(1)
        if not os.path.exists(args.topology):
            logger.critical('topology file %s does not exist')
            sys.exit(1)

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
        except KeyboardInterrupt:
            logger.critical('interrupted with Ctrl-C... bye!')
            sys.exit(0)

        scheduler = Scheduler()
        tasks = topology.get_tasks('down')
        scheduler.append(tasks)
        scheduler.run()

        topology.state.save()


command = DownCommand()
