#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.node import TopologyNode


logger = getLogger(__name__)


class Interface(TopologyNode):
    """ A interface
    """

    _KNOWN_ATTRIBUTES = {
    }

    def __init__(self, dictionary, parent=None):
        """ Initialize a machines definition
        """
        super(Interface, self).__init__(dictionary, parent)

        # get some attributes
        self._settattr_dict_defaults(dictionary, self._KNOWN_ATTRIBUTES)