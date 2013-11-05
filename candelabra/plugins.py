#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Plugins infrastructure for Candelabra..

You can add a plugin by defining an entry-point in your software distribution. For example, for a provider
for VMware, you should define an entry point like this in your `setup.py` file:

    >>> entry_points={
    >>>     'candelabra.provider': [
    >>>        'vmware_provider = candelabra_vmware.plugin:register_me',
    >>>    ]
    >>> }

Then, in your candelabra_vmware/plugin.py, there must be a register_me function like this:

    >>> from candelabra.plugins import ProviderPlugin
    >>>
    >>> class VMWareProvider(ProviderPlugin):
    >>>     MACHINE = VMWareMachine
    >>>
    >>> provider_instance = VMWareProvider()
    >>>
    >>> def register_me(registry_instance):
    >>>     registry_instance.register('vmware', provider_instance)


"""

from logging import getLogger
import os
import sys
import pkg_resources

from candelabra.config import config
from candelabra.constants import CFG_DEFAULT_PROVIDER
from candelabra.errors import TopologyException


logger = getLogger(__name__)


########################################################################################################################


class PluginsRegistry(object):
    """ A registry for plugins
    """

    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin):
        if self.validate(plugin):
            self.plugins[name] = plugin

    def validate(self, plugin):
        return True

    @property
    def names(self):
        return self.plugins.keys()


PLUGINS_REGISTRIES = {
    'candelabra.provider': PluginsRegistry(),
    'candelabra.provisioner': PluginsRegistry(),
    'candelabra.guest': PluginsRegistry(),
    'candelabra.command': PluginsRegistry(),
    'candelabra.communicator': PluginsRegistry(),
}


def register_all():
    """ Register all plugins we can find in the system.

    For each plugin, we will invoke the entry point with a :class:`PluginsRegistry` instance as the
    only parameter. Then, the entry point must call the instance :meth:`register: method in order
    to register it...
    """
    logger.debug('registering all plugins')
    for family_name, registry_instance in PLUGINS_REGISTRIES.iteritems():
        logger.debug('... looking for plugins for %s', family_name)
        for entrypoint in pkg_resources.iter_entry_points(group=family_name):
            # Grab the function that is the actual plugin.
            plugin_entrypoint = entrypoint.load()

            # Call the plugin with the data
            plugin_entrypoint(registry_instance)


########################################################################################################################

class CommandPlugin(object):
    """ A command from command line
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'

    def run(self, args, command):
        """ Run the command
        """
        raise NotImplementedError('must be implemented')

    def run_with_topology(self, args, topology_file, command=None, save_state=True):
        """ Run a command, managing the topology
        """
        if command:
            logger.info('running command "%s"', command)

        if topology_file is None:
            from candelabra.topology.root import guess_topology_file

            topology_file = guess_topology_file()

        if topology_file is None:
            logger.critical('no topology file provided')
            sys.exit(1)
        if not os.path.exists(topology_file):
            logger.critical('topology file %s does not exist', topology_file)
            sys.exit(1)

        from candelabra.errors import TopologyException, ProviderNotFoundException, CandelabraException
        from candelabra.scheduler.base import TasksScheduler

        # load the topology file and create a tree
        try:
            from candelabra.topology.root import TopologyRoot

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
                scheduler = TasksScheduler()
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


class ProviderPlugin(object):
    """ A provider
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'
    MACHINE = None              # the machine class that will be instantiated for each definition in the topology
    APPLIANCE = None            # the appliance class that will be instantiated for each definition in the topology
    INTERFACE = None
    SHARED = None
    COMMUNICATORS = None


class ProvisionerPlugin(object):
    """ A provisioner
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'
    PROVISIONER = None          # the provisioner class that will be instantiated for each machine

    def run(self, command):
        """ Run a command
        """
        raise NotImplementedError('must be implemented')


class GuestPlugin(object):
    """ A guest definition
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'


class CommunicatorPlugin(object):
    """ A communicator
    """
    NAME = 'unknown'
    DESCRIPTION = 'unknown'
    ONLY_PROVIDERS = []
    COMMUNICATOR = None                 # the communicator class that will be instantiated for each machine


########################################################################################################################

def get_provider(name):
    """ Get a ProviderPlugin for a given name
    """
    return PLUGINS_REGISTRIES['candelabra.provider'].plugins[name]


def _get_provider_class_from_dict(**kwargs):
    """ Get a a provider class from a dictionary
    """
    for name in ['class', 'cfg_class', '_class']:
        if name in kwargs:
            return kwargs[name]

    for alternative in ['_container', '_parent']:
        if alternative in kwargs:
            alternative_attr = kwargs[alternative]
            if alternative_attr:
                for name in ['class', 'cfg_class', '_class']:
                    if hasattr(alternative_attr, name):
                        return getattr(alternative_attr, name)

    return config.get_key(CFG_DEFAULT_PROVIDER)


def _get_class(_family, _attr, _name, **kwargs):
    _class_name = _get_provider_class_from_dict(**kwargs).lower()
    if not _class_name:
        raise TopologyException('internal: no %s class available' % (_name))

    try:
        _class = getattr(PLUGINS_REGISTRIES[_family].plugins[_class_name], _attr)
    except KeyError, e:
        m = 'cannot build a %s of class %s' % (_name, _class_name)
        logger.warning(m)
        raise TopologyException(m)

    return _class(**kwargs)


def build_machine_instance(**kwargs):
    """ The factory for machine that returns a subclass fo MachineNode with the right node
    """
    return _get_class('candelabra.provider', 'MACHINE', 'communicator', **kwargs)


def build_provisioner_instance(**kwargs):
    """ The factory for provisioners that returns a subclass fo Provisioner with the right node
    """
    return _get_class('candelabra.provisioner', 'PROVISIONER', 'provisioner', **kwargs)


def build_shared_instance(**kwargs):
    """ The factory for shared folders that returns a subclass fo SharedNode with the right node
    """
    return _get_class('candelabra.provider', 'SHARED', 'shared folder', **kwargs)


def build_interface_instance(**kwargs):
    """ The factory for interfaces that returns a subclass fo InterfaceNode with the right node
    """
    return _get_class('candelabra.provider', 'INTERFACE', 'interface', **kwargs)


def build_guest_instance(**kwargs):
    """ The factory for guests that returns a subclass fo Guest with the right node
    """
    return _get_class('candelabra.guest', 'GUEST', 'guest', **kwargs)


def build_communicator_instance(**kwargs):
    """ The factory for communicator that returns a subclass fo Communicator with the right node
    """
    return _get_class('candelabra.communicator', 'COMMUNICATOR', 'communicator', **kwargs)


