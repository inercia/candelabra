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

from candelabra.constants import YAML_ROOT, YAML_SECTION_DEFAULT, YAML_SECTION_MACHINES, DEFAULT_TOPOLOGY_DIR_GUESSES, DEFAULT_TOPOLOGY_FILE_GUESSES
from candelabra.errors import TopologyException
from candelabra.plugins import PLUGINS_REGISTRIES, build_machine_instance, build_interface_instance
from candelabra.topology.interface import DEFAULT_INTERFACES
from candelabra.topology.machine import MachineNode
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
        self._machines = []
        self._yaml = None
        self._global_machine = None
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
        with open(self._filename) as infile:
            y = pyaml.yaml.safe_load(infile)

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
            logger.debug('topology: ... %s', self._global_machine)
            if len(self._global_machine.cfg_interfaces) == 0:
                for iface_desc in DEFAULT_INTERFACES:
                    iface = build_interface_instance(_container=self._global_machine, **iface_desc)
                    self._global_machine.cfg_interfaces.append(iface)

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
                        if 'uuid' in machine_state:
                            logger.debug('topology: ... updating %s with saved state', machine_name)
                            machine_definition.update(machine_state)
                            logger.debug('topology: ..... UUID: %s', machine_definition['uuid'])
                        else:
                            logger.warning('data for %s in state file seems useless... ignoring', machine_name)

                    # load the machine class (ie, VirtualboxMachine)
                    machine_inst = build_machine_instance(_parent=self._global_machine, **machine_definition)
                    self._machines.append(machine_inst)

            logger.debug('topology: ... %d machines loaded', len(self._machines))

            logger.debug('topology: loaded the following machines:')
            for m in self._machines:
                logger.debug('topology: ... %s', m)
                for s in m.cfg_shared:
                    logger.debug('topology: ...... %s', s)
                for i in m.cfg_interfaces:
                    logger.debug('topology: ...... %s', i)
                for p in m.cfg_provisioner:
                    logger.debug('topology: ...... %s', p)

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