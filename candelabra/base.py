#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import sys

from candelabra.errors import TopologyException, ProviderNotFoundException, CandelabraException
from candelabra.scheduler.base import Scheduler
from candelabra.topology.root import TopologyRoot, guess_topology_file

logger = getLogger(__name__)


class Command(object):
    """ A command from command line
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'

    def run_with_topology(self, args, topology_file, command=None, save_state=True):
        """ Run a command, managing the topology
        """
        if command:
            logger.info('running command "%s"', command)

        if topology_file is None:
            topology_file = guess_topology_file()

        if topology_file is None:
            logger.critical('no topology file provided')
            sys.exit(1)
        if not os.path.exists(topology_file):
            logger.critical('topology file %s does not exist', topology_file)
            sys.exit(1)

        # load the topology file and create a tree
        try:
            topology = TopologyRoot()
            topology.load(topology_file)
        except TopologyException, e:
            logger.critical(str(e))
            sys.exit(1)
        except ProviderNotFoundException, e:
            logger.critical(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            logger.critical('interrupted with Ctrl-C... bye!')
            sys.exit(0)

        scheduler = None
        try:
            if command:
                scheduler = Scheduler()
                tasks = topology.get_tasks(command)
                assert all(isinstance(t, tuple) for t in tasks)
                scheduler.append(tasks)
                scheduler.run()
        except CandelabraException:
            raise
        except Exception, e:
            logger.critical('uncaught exception')
            raise
        finally:
            if save_state:
                if scheduler and scheduler.num_completed > 0:
                    topology.state.save()

        return topology

