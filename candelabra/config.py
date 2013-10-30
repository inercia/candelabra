#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import os
import sys
from logging import getLogger

from configparser import ConfigParser

from candelabra.constants import CONFIG_FILE_PATHS, CONFIG_FILE_PATH_CREATION, CFG_BOXES_PATH, CFG_LOG_FILE, CFG_LOG_FILE_LEVEL

logger = getLogger(__name__)

__HERE__ = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_CONFIG_FILE = os.path.join(__HERE__, 'static', 'candelabra.conf')

# replacements we will do in the config file template
_DEFAULT_CONFIG_FILE_REPLACEMENTS = {
    'DEFAULT_BOXES_PATH': os.path.expandvars(CFG_BOXES_PATH[2]),
    'DEFAULT_LOG_FILE': os.path.expandvars(CFG_LOG_FILE[2]),
    'DEFAULT_LOG_FILE_LEVEL': CFG_LOG_FILE_LEVEL[2],
}

#: methods that we map to the config object
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
        """ Load or create the config file
        """
        self.config = ConfigParser()
        self.path = os.path.expandvars(path) if path else self._find_config_path()
        if not self.path or not os.path.exists(self.path):
            self.path = os.path.expandvars(CONFIG_FILE_PATH_CREATION[sys.platform])
            self._create_default_config()

        logger.info('loading config from %s', self.path)

        self.config.read([self.path])

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

    def _create_default_config(self):
        """ Create a default config file
        """
        logger.debug('creating config file in %s', self.path)
        b = os.path.dirname(self.path)
        if not os.path.exists(b):
            os.makedirs(b)

        with open(_DEFAULT_CONFIG_FILE, 'r') as input_f:
            with open(self.path, 'w') as output_f:
                output_f.write(input_f.read().format(**_DEFAULT_CONFIG_FILE_REPLACEMENTS))

    def get_key(self, k, default=None):
        """ Get a configuration key
        """
        if len(k) == 2:
            return self.get(k[0], k[1], fallback=default)
        elif len(k) == 3:
            return self.get(k[0], k[1], fallback=k[2])
        else:
            return self.get(k[0], fallback=default)


config = CandelabraConfig()

