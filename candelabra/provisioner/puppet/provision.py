#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger


logger = getLogger(__name__)

COMMAND = """
puppet apply --modulepath '{modules}' --manifestdir {manifests} --detailed-exitcodes {init_pp} || [ $? -eq 2 ]
"""
