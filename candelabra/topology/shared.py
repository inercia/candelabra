#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.node import TopologyNode

logger = getLogger(__name__)


class Shared(TopologyNode):
    """ A shared for a machine
    """

    # known attributes
    # the right value is either:
    # - a constructor (and default value will be obtained from parent)
    # - tuple is the constructor and a default value
    __known_attributes = {
        'local': (str, ''),
        'remote': (str, ''),
        'writable': (bool, True),
        'automount': (bool, True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(Shared, self).__init__(_parent=_parent, **kwargs)
        self._settattr_dict_defaults(kwargs, self.__known_attributes)
