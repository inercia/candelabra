#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A provisioner node in the topology.

Provsioners must belong to machines, so their container must be a :class:`MachineNode`.
"""

from logging import getLogger

from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)


class ProvisionerNode(TopologyNode):
    """ A provisioner for a machine
    """

    __known_attributes = [
    ]

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a provisioner node
        """
        super(ProvisionerNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

        # private attributes
        self._num = self.get_inc_counter(self.machine, "cfg_provisioners")

    #####################
    # properties
    #####################

    @property
    def machine(self):
        """ Return the machine where this insterface s installed
        :returns: a :class:`MachineNode`: instance
        """
        return self._container
