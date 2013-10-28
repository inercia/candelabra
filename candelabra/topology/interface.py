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

    def __init__(self, dictionary, parent=None):
        """ Initialize a interface definition
        """
        super(Interface, self).__init__(dictionary, parent)

        self._hostname = dictionary.get("hostname", None)
        self._network = dictionary.get("network", None)

