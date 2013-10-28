#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class TopologyNode(object):
    """ A topology node
    """

    def __init__(self, dictionary, parent=None):
        """ Initialize a topology node
        """
        self.name = dictionary.get("name", None)
        self.clas = dictionary.get("class", None)

        self.parent = parent

    def __repr__(self):
        return '<%s [name:%s, class:%s]>' % (self.__class__.__name__, self.name, self.clas)

    def __str__(self):
        return 'name:%s class:%s' % (self.name, self.clas)

    def __getattr__(self, item):
        return getattr(self.parent, item)