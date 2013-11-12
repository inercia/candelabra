#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
The topology hierarchy root.

The topology root represents the top element in the topology hierarchy. It has two important attributes:

* the global machine, a parent machine definition used for setting global attributes.
* the list of machines defined in the topology.

The root provides some convenience methods for running a task on all the nodes in the tree. See :meth:`get_tasks`
"""

from logging import getLogger
import os
import pyaml
import yaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_DEFAULT, YAML_SECTION_MACHINES, DEFAULT_TOPOLOGY_DIR_GUESSES, DEFAULT_TOPOLOGY_FILE_GUESSES, YAML_SECTION_NETWORKS
from candelabra.errors import TopologyException
from candelabra.plugins import build_machine_instance, build_interface_instance, build_network_instance
from candelabra.topology.interface import DEFAULT_INTERFACES
from candelabra.topology.network import DEFAULT_NETWORKS
from candelabra.topology.state import State

logger = getLogger(__name__)


def guess_topology_file(extra=[]):
    """ Try to guess the topology file
    """
    for directory in DEFAULT_TOPOLOGY_DIR_GUESSES:
        for filename in DEFAULT_TOPOLOGY_FILE_GUESSES:
            filename = os.path.expandvars(os.path.join(directory, filename))
            if os.path.isfile(filename):
                return filename

    for filename in extra:
        if os.path.isfile(filename):
            return filename

    return None


class TopologyRoot(object):
    """ Topology definition
    """

    def __init__(self):
        """ Initialize a topology definition
        """
        self._filename = None
        self._yaml = None
        self._global_machine = None
        self._networks = []
        self._machines = []
        self._state = State(self)

    def load(self, filename):
        """ Load the topology from a YAML file
        """
        self._filename = filename

        if self._state.persisted:
            self._state.load()
        else:
            logger.info('no previous state found for this topology')

        logger.info('topology: loading from "%s"...', self._filename)
        try:
            with open(self._filename) as infile:
                y = pyaml.yaml.safe_load(infile)
        except yaml.scanner.ScannerError, e:
            raise TopologyException('malformed topology file: %s' % str(e))

        try:
            self._yaml = y[YAML_ROOT]
        except KeyError, e:
            raise TopologyException('topology definition error: "%s" key not found' % str(e))

        # load the default section and create a "global machine"
        # all machines will refer to this global machine when they do not find some attribute
        if YAML_SECTION_DEFAULT in self._yaml:
            logger.debug('topology: loading globals...')
            global_dict = self._yaml[YAML_SECTION_DEFAULT]
            self._global_machine = build_machine_instance(**global_dict)

            # create all the default networks
            default_networks = [build_network_instance(_container=self._global_machine, **desc)
                                for desc in DEFAULT_NETWORKS]

            # process all the networks found in the topology file, and add them to the global machine
            global_networks = []
            if YAML_SECTION_NETWORKS in self._yaml:
                logger.debug('topology: loading networks...')
                networks_list = self._yaml[YAML_SECTION_NETWORKS]
                for network in networks_list:
                    if 'network' in network:
                        network_definition = network['network']
                        network_inst = build_network_instance(_container=self._global_machine, **network_definition)
                        global_networks.append(network_inst)

            self._global_machine.cfg_networks = default_networks + global_networks

            # add the default network interfaces to the global machine (the default interfaces are added first)
            default_ifaces = [build_interface_instance(_container=self._global_machine, **desc)
                              for desc in DEFAULT_INTERFACES]
            self._global_machine.cfg_interfaces = default_ifaces + self._global_machine.cfg_interfaces

            # done! we have the global machine ready!!
            logger.debug('topology: global machine:')
            self._global_machine.pretty_print(prefix='topology:')

        # process all the machines found in the topology file
        if YAML_SECTION_MACHINES in self._yaml:
            logger.debug('topology: loading machines...')
            machines_list = self._yaml[YAML_SECTION_MACHINES]
            for machine in machines_list:
                if 'machine' in machine:
                    machine_definition = machine['machine']
                    machine_name = machine_definition['name']

                    # try to locate the state file...
                    machine_state = self._state.get_machine_state(machine_name)
                    if machine_state:
                        # check if there is some valid information for this machine, like a valid UUID
                        if 'uuid' in machine_state:
                            logger.debug('topology: ... updating %s with saved state', machine_name)
                            machine_definition.update(machine_state)
                            logger.debug('topology: ..... UUID: %s', machine_definition['uuid'])
                        else:
                            logger.warning('data for %s in state file seems useless... ignoring', machine_name)

                    # get the right instance for this machine class (ie, VirtualboxMachine)
                    machine_inst = build_machine_instance(_parent=self._global_machine, **machine_definition)
                    self._machines.append(machine_inst)

            logger.debug('topology: ... %d machines loaded', len(self._machines))

            logger.debug('topology: loaded the following machines:')
            for m in self._machines:
                m.pretty_print(prefix='topology:')

    @property
    def state(self):
        """ Get the state for all machines in the topology
        """
        return self._state

    @property
    def machines(self):
        return self._machines

    def get_tasks(self, task_name):
        """ Get all tasks needed for running something in all machines
        """
        logger.debug('getting tasks for running "%s" on %d machines', task_name, len(self._machines))
        method_name = 'get_tasks_%s' % task_name
        res = []
        for machine in self._machines:
            try:
                tasks_gen = getattr(machine, method_name)
            except AttributeError:
                logger.debug('nothing to do for "%s" in "%s"', task_name, machine)
                continue
            else:
                machine.clear_tasks()
                tasks_gen()
                new_tasks = machine.get_tasks()
                assert all(isinstance(t, tuple) for t in new_tasks)
                num_new_tasks = len(new_tasks)
                if num_new_tasks:
                    logger.debug('adding %d required tasks', num_new_tasks)
                    res += new_tasks

        return res

    def get_machine_by_uuid(self):
        """ Get a machine by UUID
        """
        pass