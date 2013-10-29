#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import yaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_DEFAULT, YAML_SECTION_MACHINES
from candelabra.errors import TopologyException
from candelabra.loader import load_machine_for_class
from candelabra.topology.machine import Machine

logger = getLogger(__name__)


class TopologyRoot(object):
    """ Topology definition
    """

    def __init__(self):
        """ Initialize a topology definition
        """
        self._machines = []
        self._yaml = None
        self._global_machine = None

    def load(self, infile):
        logger.info('loading from "%s"...', infile.name)
        y = yaml.safe_load(infile)

        logger.debug('loaded:')
        for line in yaml.safe_dump(y).splitlines():
            logger.debug('    %s', line)

        try:
            self._yaml = y[YAML_ROOT]
        except KeyError, e:
            raise TopologyException('topology definition error: "%s" key not found' % str(e))

        if YAML_SECTION_DEFAULT in self._yaml:
            logger.debug('loading globals...')
            global_dict = self._yaml[YAML_SECTION_DEFAULT]
            self._global_machine = Machine(global_dict)
            logger.debug('    %s', self._global_machine)

        if YAML_SECTION_MACHINES in self._yaml:
            logger.debug('loading machines...')
            machines_list = self._yaml[YAML_SECTION_MACHINES]
            for machine in machines_list:
                if 'machine' in machine:
                    machine_definition = machine['machine']
                    try:
                        machine_class_str = machine_definition['class']
                    except KeyError, e:
                        raise TopologyException(
                            'topology definition error: "class" key not found for machine "%s"' % machine_definition)

                    machine_class = load_machine_for_class(machine_class_str)
                    if not machine_class:
                        logger.warning('   unknown machine class "%s"!!!', machine_class_str)
                    else:
                        machine_inst = machine_class(machine_definition, parent=self._global_machine)

                        self._machines.append(machine_inst)

            logger.debug('    %d machines loaded', len(self._machines))

            for m in self._machines:
                logger.debug('       %s', m)

    def get_tasks(self, task_name):
        """ Run a task name in all machines
        """
        logger.debug('getting tasks for running %s on %d machines', task_name, len(self._machines))
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
                logger.debug('adding %d tasks', len(new_tasks))
                res += new_tasks

        return res
