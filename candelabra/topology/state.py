#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
import os

from weakref import proxy
from logging import getLogger
import pyaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_MACHINES, STATE_FILE_EXTENSION
from candelabra.errors import TopologyException

logger = getLogger(__name__)


class State(object):
    """ Topology definition
    """

    def __init__(self, topology):
        """ Initialize a topology definition
        """
        self._machines = {}
        self._yaml = None
        self._filename = None
        self._topology = proxy(topology)

    def load(self):
        """ Load the state from a persisted file
        """
        logger.info('state: loading from "%s"...', self.filename)
        with open(self.filename) as input_file:
            input_contents = input_file.read()
            y = pyaml.yaml.safe_load(input_contents)

        try:
            self._yaml = y[YAML_ROOT]
        except KeyError, e:
            raise TopologyException('topology definition error: "%s" key not found' % str(e))

        if YAML_SECTION_MACHINES in self._yaml:
            logger.debug('state: loading state for machines...')
            machines_list = self._yaml[YAML_SECTION_MACHINES]
            for machine in machines_list:
                if 'machine' in machine:
                    machine_definition = machine['machine']
                    machine_name = machine_definition['name']
                    self._machines[machine_name] = machine_definition
            logger.debug('state: ... %d machines loaded:', len(self._machines))

            for m in self._machines.values():
                logger.debug('state: ...... %s', m)

    def save(self):
        """ Save the state to a persisted file
        """
        output = {}
        output[YAML_ROOT] = {}
        output[YAML_ROOT][YAML_SECTION_MACHINES] = []

        logger.debug('saving topology state:')
        with open(self.filename, 'w+') as output_file:
            for machine in self._topology._machines:
                machine_definition = {}
                machine_definition['machine'] = machine.get_state_dict()
                output[YAML_ROOT][YAML_SECTION_MACHINES].append(machine_definition)

            output_file.write(pyaml.dump(output))

        logger.debug('state saved as %s', self.filename)

    @property
    def filename(self):
        """ Return the filename for the persisted state file
        """
        if not self._filename:
            file_name, file_extension = os.path.splitext(self._topology._filename)
            self._filename = "%s.%s" % (file_name, STATE_FILE_EXTENSION)
        return self._filename

    @property
    def persisted(self):
        """ Return True if there is a persisted state file on disc
        """
        return bool(os.path.exists(self.filename))

    def get_machine_state(self, machine):
        """ Return a dictionary with the state for a machine
        """
        if machine in self._machines:
            return self._machines[machine]
        else:
            return {}
