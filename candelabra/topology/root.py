#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import yaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_GLOBAL, YAML_SECTION_MACHINES
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

        if YAML_SECTION_GLOBAL in self._yaml:
            logger.debug('loading globals...')
            global_dict = self._yaml[YAML_SECTION_GLOBAL]
            self._global_machine = Machine(global_dict)
            logger.debug('    %s', self._global_machine)

        if YAML_SECTION_MACHINES in self._yaml:
            machines_dict = self._yaml[YAML_SECTION_MACHINES]
            logger.debug('loading machines...')
            for machine in machines_dict:
                try:
                    machine_class_str = machine['class']
                except KeyError, e:
                    raise TopologyException('topology definition error: "class" key not found for machine "%s"' % machine)

                machine_class = load_machine_for_class(machine_class_str)
                machine_inst = machine_class(machine, parent=self._global_machine)

                self._machines.append(machine_inst)
            logger.debug('    %d machines loaded', len(self._machines))

            for m in self._machines:
                logger.debug('       %s', m)

