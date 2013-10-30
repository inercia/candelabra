#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import pyaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_DEFAULT, YAML_SECTION_MACHINES, DEFAULT_TOPOLOGY_DIR_GUESSES, DEFAULT_TOPOLOGY_FILE_GUESSES
from candelabra.errors import TopologyException
from candelabra.loader import load_provider_machine_for
from candelabra.topology.machine import Machine
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

        # logger.debug('topology: loaded:')
        # for line in yaml.safe_dump(y).splitlines():
        #     logger.debug('topology: ... %s', line)

        try:
            self._yaml = y[YAML_ROOT]
        except KeyError, e:
            raise TopologyException('topology definition error: "%s" key not found' % str(e))

        if YAML_SECTION_DEFAULT in self._yaml:
            logger.debug('topology: loading globals...')
            global_dict = self._yaml[YAML_SECTION_DEFAULT]
            self._global_machine = Machine(global_dict)
            logger.debug('topology: ... %s', self._global_machine)

        if YAML_SECTION_MACHINES in self._yaml:
            logger.debug('topology: loading machines...')
            machines_list = self._yaml[YAML_SECTION_MACHINES]
            for machine in machines_list:
                if 'machine' in machine:
                    machine_definition = machine['machine']
                    machine_name = machine_definition['name']
                    machine_state = self._state.get_machine_state(machine_name)
                    if machine_state:
                        logger.debug('topology: ... updating %s with saved state', machine_name)
                        machine_definition.update(machine_state)
                        logger.debug('topology: ..... UUID: %s', machine_definition['uuid'])
                    try:
                        machine_class_str = machine_definition['class']
                    except KeyError, e:
                        raise TopologyException(
                            'topology definition error: "class" key not found for machine "%s"' % machine_definition)

                    machine_class = load_provider_machine_for(machine_class_str)
                    if not machine_class:
                        logger.warning('topology: ... unknown machine class "%s"!!!', machine_class_str)
                    else:
                        machine_inst = machine_class(machine_definition, parent=self._global_machine)

                        self._machines.append(machine_inst)

            logger.debug('topology: ... %d machines loaded', len(self._machines))

            for m in self._machines:
                logger.debug('topology: ... %s', m)

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
                new_tasks = tasks_gen()
                num_new_tasks = len(new_tasks)
                if num_new_tasks:
                    logger.debug('adding %d tasks', num_new_tasks)
                    res += new_tasks

        return res

    def get_machine_by_uuid(self):
        """ Get a machine by UUID
        """
        pass