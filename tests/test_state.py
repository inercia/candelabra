#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import unittest
import logging

from candelabra.topology.machine import MachineNode

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class StateTestSuite(unittest.TestCase):
    """ Test suite for states
    """

    def test_nodes(self):
        """ Testing tha we can manage nodes attributes
        """
        vm1 = MachineNode(name='vm1', uuid='some-uuid')
        state = vm1.get_state_dict()
        self.assertTrue(isinstance(state, dict))
        self.assertTrue('name' in state, 'state=%s' % str(state))
        self.assertTrue('uuid' in state, 'state=%s' % str(state))
        self.assertTrue('state' not in state, 'state=%s' % str(state))
        self.assertEqual(state['name'], 'vm1', 'state=%s' % str(state))


