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
# config file


class ConfigFileMissingException(CandelabraException):
    pass

#########################################
# machines


class MachineException(CandelabraException):
    pass


class MachineDefinitionException(MachineException):
    pass


#########################################
# topologies

class TopologyException(CandelabraException):
    pass

#########################################
# providers


class ProviderException(CandelabraException):
    pass


class ProviderNotFoundException(ProviderException):
    pass


#########################################
# scheduling and execution

class SchedulerTaskException(CandelabraException):
    pass

#########################################
# images

class ImportException(CandelabraException):
    pass

