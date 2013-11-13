#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import logging
from candelabra.provider.virtualbox import VirtualboxMachineNode

from candelabra.tests import CandelabraTestBase
from candelabra.topology.root import TopologyRoot, DEFAULT_NAT_INTERFACE_NAME

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MachineParsingTestSuite(CandelabraTestBase):
    """ Test suite for machines parsing
    """

    def test_parsing1(self):
        DEFINITION = """
            candelabra:
                default:
                    class:                      virtualbox
                    box:
                        class:                  vagrant
                        name:                   test
                        url:                    http://shonky.info/centos64.box
                    provisioners:
                        - class:                puppet
                          manifest:             puppet/manifest1.pp
                        - class:                puppet
                          manifest:             puppet/manifest2.pp
                    shared:
                        - local:                docs
                          remote:               /home/docs
                        - local:                $HOME
                          remote:               /home/host_home
                networks:
                    - network:
                            scope:              private
                            name:               net1

                    - network:
                            scope:              private
                            name:               net2
                machines:
                    - machine:
                            name:               vm1
                            hostname:           vm1
                            gui:                gui
                            interfaces:
                                - name:         iface-1
                                  connected:    net1
                                - name:         iface-2
                                  connected:    net2
        """
        root = TopologyRoot()
        root.load_str(DEFINITION)

        # check the global machine
        global_machine = root.get_global_machine()
        self.assertIsNotNone(global_machine)
        self.assertGreaterEqual(len(global_machine.cfg_networks), 2)    # there can be some default networks

        # check the machine and some basic properties
        vm1_machine = root.get_machine_by_name('vm1')
        self.assertGreaterEqual(len(root.machines), 0)
        self.assertIsNotNone(vm1_machine)
        self.assertIsInstance(vm1_machine, VirtualboxMachineNode)
        self.assertEquals(vm1_machine.cfg_gui, 'gui')

        # check the networks in VM1 are references to the global networks
        global_networks_ids = {id(x) for x in global_machine.cfg_networks}
        self.assertIn(id(vm1_machine.cfg_networks[0]), global_networks_ids)
        self.assertIn(id(vm1_machine.cfg_networks[1]), global_networks_ids)

        # check the network interfaces
        expected_ifaces_names = [DEFAULT_NAT_INTERFACE_NAME, 'iface-1', 'iface-2']
        self.assertGreaterEqual(len(vm1_machine.cfg_interfaces), 2)
        self.assertNotEqual(vm1_machine.cfg_interfaces[0].cfg_name, vm1_machine.cfg_interfaces[1].cfg_name)
        self.assertIn(vm1_machine.cfg_interfaces[0].cfg_name, expected_ifaces_names)
        self.assertIn(vm1_machine.cfg_interfaces[1].cfg_name, expected_ifaces_names)


