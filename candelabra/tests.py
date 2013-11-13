#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import os
import unittest

from candelabra.config import config
from candelabra.plugins import register_all


class CandelabraTestBase(unittest.TestCase):
    """ Base class for unit tests
    """

    CONFIG = ""

    @classmethod
    def setUpClass(cls):
        config.load_string(cls.CONFIG)
        register_all()


#: skip a unit test if running in Travis CI
skipTravis = lambda x: unittest.skipIf(os.environ.get('TRAVIS', '').lower() in ['true', 'yes', '1'],
	                                   'running in Travis-CI')

