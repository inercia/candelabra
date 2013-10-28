#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


def argparser(parser):
    """ Parse arguments
    """
    parser.add_argument('--timeout',
                        type=int,
                        help='timeout for the bringing up the machines')


