#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A shared folder node in the topology.

Shared folders must belong to machines, so their container must be a :class:`MachineNode`.
"""

from logging import getLogger
import os

from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)


def _path_norm(path):
    """ Returns a normalized version of a path
    """
    return os.path.abspath(os.path.expandvars(path))


class SharedNode(TopologyNode):
    """ A shared folder for a machine.
    """

    # known attributes
    # the right value is either:
    # - a constructor (and default value will be obtained from parent)
    # - tuple is the constructor and a default value
    __known_attributes = [
        TopologyAttribute('local', _path_norm, default='', copy=True),
        TopologyAttribute('remote', _path_norm, default='', copy=True),
        TopologyAttribute('writable', bool, default=True, copy=True),
        TopologyAttribute('create_if_missing', bool, default=True, copy=True),
        TopologyAttribute('owner', str, default='vagrant', copy=True),
        TopologyAttribute('group', str, default='vagrant', copy=True),
        TopologyAttribute('mode', int, default=755, copy=True),
    ]

    def __init__(self, **kwargs):
        """ Initialize a topology node
        """
        super(SharedNode, self).__init__(**kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # private attributes
        self._num = self.get_inc_counter(self.machine, "cfg_shared")

    #####################
    # properties
    #####################

    @property
    def machine(self):
        """ Return the machine where this insterface s installed
        :returns: a :class:`MachineNode`: instance
        """
        return self._container

    #####################
    # tasks
    #####################

    def do_shared_create(self):
        logger.debug('creating shared folder: nothing to do')

    def do_shared_mount(self):
        logger.debug('mounting shared folder: nothing to do')
