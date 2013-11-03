#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import unittest
import logging

from candelabra.topology.node import TopologyNode, TopologyAttribute

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class NodeTestSuite(unittest.TestCase):
    """ Test suite for nodes
    """

    def test_nodes(self):
        """ Testing tha we can manage nodes attributes
        """

        class TestNode(TopologyNode):
            def __init__(self, _parent=None, **kwargs):
                super(TestNode, self).__init__(_parent=_parent, **kwargs)
                TopologyAttribute.setall(self, kwargs, self.__known_attributes)

            __known_attributes = {
                'a': TopologyAttribute(constructor=str, copy=True),
                'b': TopologyAttribute(constructor=int, copy=True),
            }

        node1 = TestNode(a=8, b=9)
        self.assertTrue(isinstance(node1.cfg_a, str), 'a has type %s' % str(type(node1.cfg_a)))
        self.assertTrue(isinstance(node1.cfg_b, int), 'b has type %s' % str(type(node1.cfg_b)))
        self.assertEqual(node1.cfg_a, '8')
        self.assertEqual(node1.cfg_b, 9)

        node2 = TestNode(a=8, _parent=node1)
        self.assertEqual(node2.cfg_a, '8')
        self.assertEqual(node2.cfg_b, 9)





