#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

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



