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
    __known_attributes = {
        'local': TopologyAttribute(constructor=_path_norm, default='', copy=True),
        'remote': TopologyAttribute(constructor=_path_norm, default='', copy=True),
        'writable': TopologyAttribute(constructor=bool, default=True, copy=True),
        'create_if_missing': TopologyAttribute(constructor=bool, default=True, copy=True),
        'owner': TopologyAttribute(constructor=str, default='vagrant', copy=True),
        'group': TopologyAttribute(constructor=str, default='vagrant', copy=True),
        'mode': TopologyAttribute(constructor=int, default=755, copy=True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(SharedNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

    #####################
    # tasks
    #####################

    def do_shared_create(self):
        logger.debug('creating shared folder: nothing to do')

    def do_shared_mount(self):
        logger.debug('mounting shared folder: nothing to do')
