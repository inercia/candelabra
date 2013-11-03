#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A network interface in the topology.

Network interfaces must belong to a Machine, so they must be contained in a :class:`MachineNode` instance.
"""

from logging import getLogger

from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)


class InterfaceNode(TopologyNode):
    """ A machine network interface

    Some important attributes:
    * the **ip** address, that can be a numeric IP, a host name, or some reserved words like *automatic*
    * the interace name, **ifname**.
    """

    __known_attributes = {
        'ip': TopologyAttribute(constructor=str, default='', copy=True),
        'ifname': TopologyAttribute(constructor=str, default='', copy=True),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a network interface in the machine
        """
        super(InterfaceNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)
