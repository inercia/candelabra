#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from candelabra.topology.node import TopologyAttribute

from candelabra.topology.provisioner import ProvisionerNode

logger = getLogger(__name__)

PUPPET_APPLY_COMMAND = """
puppet apply --modulepath '{modules}' --manifestdir {manifests} --detailed-exitcodes {init_pp} || [ $? -eq 2 ]
"""

class PuppetProvisioner(ProvisionerNode):
    """ A Puppet provisioner
    """

    # known attributes
    # the right value is either:
    # - a constructor (and default value will be obtained from parent)
    # - tuple is the constructor and a default value
    __known_attributes = [
        TopologyAttribute('init_pp', str, default='', inherited=True),
        TopologyAttribute('manifest', str, default='', inherited=True),
        TopologyAttribute('modules', str, default='', inherited=True),
        TopologyAttribute('command', str, default=PUPPET_APPLY_COMMAND, inherited=True),
    ]

    # attributes that are saved in the state file
    _state_attributes = {
    }

    def __init__(self, **kwargs):
        """ Initialize a VirtualBox machine
        """
        super(PuppetProvisioner, self).__init__(**kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)
