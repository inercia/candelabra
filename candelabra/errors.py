#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class CandelabraException(Exception):
    pass

#########################################


class MachineException(CandelabraException):
    pass


class MachineDefinitionException(MachineException):
    pass


#########################################

class TopologyException(CandelabraException):
    pass
