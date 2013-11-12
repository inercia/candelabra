#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Topology state.

This module is responsible for saving the current toplogy nodes state, as well as restorying a previously
saved dump of the state.
"""

import os

from weakref import proxy
from logging import getLogger
import pyaml

from candelabra.constants import YAML_ROOT, YAML_SECTION_MACHINES, STATE_FILE_EXTENSION
from candelabra.errors import TopologyException, MalformedStateFileException

logger = getLogger(__name__)


class State(object):
    """ State definition

    State definition is kept in memory _as a dictionary_, not as a tree of topology :class:`Node`:
    """

    def __init__(self, topology):
        """ Initialize a state.
        """
        self._machines = {}
        self._yaml = None
        self._filename = None
        self._topology = proxy(topology)

    def load(self):
        """ Load the state from a persisted file

        The state file is kept in memory as a dictionary, not as a tree of topology :class:`Node`:
        """
        logger.info('state: loading from "%s"...', self.filename)
        with open(self.filename) as input_file:
            input_contents = input_file.read()
            if len(input_contents) == 0:
                logger.warning('state: state file is present but empty!!')
                logger.warning('state: you should check it and/or remove it.')
                raise MalformedStateFileException('invalid state file.')

            y = pyaml.yaml.safe_load(input_contents)

        if not y:
            logger.warning('state: could not parse the state file.')
            logger.warning('state: you should check it and/or remove it.')
            raise MalformedStateFileException('invalid state file.')

        try:
            self._yaml = y[YAML_ROOT]
        except KeyError, e:
            raise TopologyException('state file error: "%s" key not found' % str(e))

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
        machines_states = []
        logger.info('saving topology state...')
        for machine in self._topology._machines:
            machine_definition = {}
            machine_state = machine.get_state_dict()
            if machine_state:
                machine_definition['machine'] = machine_state
                machines_states.append(machine_definition)

        if len(machines_states) > 0:
            output = {}
            output[YAML_ROOT] = {}
            output[YAML_ROOT][YAML_SECTION_MACHINES] = machines_states
            with open(self.filename, 'w+') as output_file:
                output_file.write(pyaml.dump(output))
            logger.debug('... state saved as %s', self.filename)
        else:
            logger.info('... no state saved: no machines reported valid state')

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

    def remove(self):
        """ Remove the state file, if it exists
        """
        if self._filename:
            try:
                os.remove(self._filename)
            except IOError:
                pass
