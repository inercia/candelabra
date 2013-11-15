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


class ConfigFileNotLoadedException(CandelabraException):
    """ The configuration file has not been loaded
    """
    pass


class ConfigFileMissingException(CandelabraException):
    """ The configuration file is missing
    """
    pass


class ComponentNotFoundException(CandelabraException):
    """ A component (ie, a plugin) is missing
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


class MachineNetworkSetupException(MachineException):
    """ An error happened when trying to setup the network in a machine
    """
    pass

#########################################
# comunicator


class CommunicatorException(CandelabraException):
    """ Communicator error
    """
    pass


class CommunicatorNotConnectedException(CommunicatorException):
    """ Communicator not connected error
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


class MalformedStateFileException(TopologyException):
    """ Malfomed state file
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
