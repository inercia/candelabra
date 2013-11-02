#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Plugins support.

You can add a plugin by defining a new entry-point. For example, for a provider for VMware we would have:

    entry_points={
        'candelabra.provider': [
            'vmware_provider = candelabra_vmware.plugin:register_me,
        ]
    },

Then, in your candelabra_vmware/plugin.py, there must be a register_me function like this:

    >>> class VMWareProvider(object):
    >>>     pass
    >>>
    >>> provider_instance = VMWareProvider()
    >>>
    >>> def register_me(registry_instance):
    >>>     registry_instance.register('vmware', provider_instance)


"""

from logging import getLogger

import pkg_resources


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


