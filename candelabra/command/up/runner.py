#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


def run(args, topology, command):
    """ Run the command
    """
    logger.info('running command "%s"', command)
    topology.run('up')