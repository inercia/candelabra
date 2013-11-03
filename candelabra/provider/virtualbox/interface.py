#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.topology.interface import InterfaceNode
from candelabra.topology.node import TopologyAttribute

logger = getLogger(__name__)


class VirtualboxInterfaceNode(InterfaceNode):
    """ A VirtualBox interface
    """

    # known attributes
    # the right value is either:
    # - a constructor (and default value will be obtained from parent)
    # - tuple is the constructor and a default value
    __known_attributes = {
        'ip': TopologyAttribute(constructor=str, default='', copy=True),
        'ifname': TopologyAttribute(constructor=str, default='', inherited=True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(VirtualboxInterfaceNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)
