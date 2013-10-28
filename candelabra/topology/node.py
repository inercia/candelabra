#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class TopologyNode(object):
    """ A topology node

    Topology nodes must react to commands by providing methods named `get_tasks_<COMMAND>` that return a list
    of tuples (:class:`Task`, :class:`Task`)
    """

    def __init__(self, dictionary, parent=None):
        """ Initialize a topology node
        """
        self.name = dictionary.get("name", None)
        self.clas = dictionary.get("class", None)
        self.parent = parent

    #####################
    # attributes
    #####################

    def __getattr__(self, item):
        if self.parent:
            return getattr(self.parent, item)
        else:
            raise AttributeError('"%s" not found' % item)

    def _settattr_if_dict(self, dictionary, attr):
        """ Set an attribute `attr` if found in a dictionary
        """
        if attr in dictionary:
            setattr(self, attr, dictionary[attr])

    def _settattr_dict_defaults(self, dictionary, defaults):
        """ Set attributes from a dictionary if they are found in the `defaults` as known attributes
        """
        for k, v in defaults.iteritems():
            self._settattr_if_dict(dictionary, k)

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        if self.name and self.clas:
            return '<%s [name:%s, class:%s] at %x>' % (self.__class__.__name__, self.name, self.clas, id(self))
        else:
            return '<%s at %x]>' % (id(self))

    def __str__(self):
        return 'name:%s class:%s' % (self.name, self.clas)
