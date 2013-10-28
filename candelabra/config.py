#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import os
import sys
from logging import getLogger

from configparser import ConfigParser

from candelabra.constants import CONFIG_FILE_PATHS, CONFIG_FILE_PATH_CREATION, DEFAULT_STORAGE_PATH, DEFAULT_CFG_SECTION_VIRTUALBOX, DEFAULT_CFG_SECTION_PUPPET

logger = getLogger(__name__)

_DEFAULT_CONFIG_FILE_CONTENTS = """
##############################################
# candelabra configuration file
##############################################
[candelabra]

# the default storage path
storage_path = {DEFAULT_STORAGE_PATH}

##############################################
[{DEFAULT_CFG_SECTION_PUPPET}]

##############################################
[{DEFAULT_CFG_SECTION_VIRTUALBOX}]

##############################################
[candelabra:logging]
level = INFO
"""

# replacements we will do in the config file template
_DEFAULT_CONFIG_FILE_REPLACEMENTS = {
    'DEFAULT_STORAGE_PATH': DEFAULT_STORAGE_PATH[sys.platform],
    'DEFAULT_CFG_SECTION_VIRTUALBOX': DEFAULT_CFG_SECTION_VIRTUALBOX,
    'DEFAULT_CFG_SECTION_PUPPET': DEFAULT_CFG_SECTION_PUPPET,
}

_CONFIG_MAPPED_METHODS = [
    'set',
    'get',
    'getint',
    'getfloat',
    'getboolean',
    'items',
    'options',
    'sections',
    'add_section',
    'has_section',
]


class CandelabraConfig(object):
    """ The candelabra config file
    """

    def __init__(self):
        self.path = None

    def load(self, path=None):
        self.config = ConfigParser()
        filename = os.path.expandvars(path) if path else self._find_config_path()
        if not filename or not os.path.exists(filename):
            filename = os.path.expandvars(CONFIG_FILE_PATH_CREATION[sys.platform])
            self._create_default_config(filename)

        logger.info('loading config from %s', filename)
        self.path = filename
        self.config.read([filename])

        for method in _CONFIG_MAPPED_METHODS:
            setattr(self, method, getattr(self.config, method))

    def _find_config_path(self):
        """ Find the config file, if it is already present in the system
        """
        for possible_path in CONFIG_FILE_PATHS:
            possible_path = os.path.expandvars(possible_path)
            if os.path.exists(possible_path):
                return possible_path
        return None

    def _create_default_config(self, filename):
        """ Create a default config file
        """
        logger.debug('creating config file in %s', filename)
        b = os.path.dirname(filename)
        if not os.path.exists(b):
            os.makedirs(b)

        with open(filename, 'w') as f:
            f.write(_DEFAULT_CONFIG_FILE_CONTENTS.format(**_DEFAULT_CONFIG_FILE_REPLACEMENTS))


config = CandelabraConfig()
