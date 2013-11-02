#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.node import TopologyNode

logger = getLogger(__name__)


class Interface(TopologyNode):
    """ A machine interface
    """

    # known attributes
    # the right value is either:
    # - a constructor (and default value will be obtained from parent)
    # - tuple is the constructor and a default value
    __known_attributes = {
        'ip': (str, ''),
        'ifname': (str, ''),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(Interface, self).__init__(_parent=_parent, **kwargs)
        self._settattr_dict_defaults(kwargs, self.__known_attributes)
