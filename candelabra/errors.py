#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class CandelabraException(Exception):
    """ Root exception for all the Candelabra errors
    """
    pass


#########################################
# usage and config file


class UnsupportedCommandException(CandelabraException):
    """ Unsupported command
    """
    pass


class ConfigFileMissingException(CandelabraException):
    """ The configuration file is missing
    """
    pass


#########################################
# machines


class MachineException(CandelabraException):
    """ Machine error
    """
    pass


class MachineDefinitionException(MachineException):
    """ Machine definition error
    """
    pass


class MachineChangeException(MachineException):
    """ An error happened when trying to change a machine
    """
    pass

#########################################
# topologies


class TopologyException(CandelabraException):
    """ Topology error
    """
    pass


class MalformedTopologyException(TopologyException):
    """ Malfomed topology error
    """
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
    """ Scheduler error
    """
    pass

#########################################
# boxes and images


class ImportException(CandelabraException):
    """ Box import error
    """
    pass


class UnsupportedBoxException(CandelabraException):
    """ Unsupported box or not recognized error
    """
    pass


class MissingBoxException(CandelabraException):
    """ Missing box or not recognized error
    """
    pass
