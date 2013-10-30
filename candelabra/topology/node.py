#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class TopologyNode(object):
    """ Base class for all topology nodes.

    Attributes
    ----------
    All known attributed will be loaded from the topology wile and added to the current instance with
    the 'cfg_' prefix. For example, if 'hostname' is a known attribute, it will be set for the
    instance under the name 'cfg_hostname'

    Commands
    --------
    Topology nodes must react to commands by providing methods named `get_tasks_<COMMAND>` that return a list
    of tuples (:class:`Task`, :class:`Task`)
    """

    def __init__(self, dictionary, parent=None):
        """ Initialize a topology node
        """
        self.cfg_name = dictionary.get("name", None)
        self.cfg_class = dictionary.get("class", None)
        self.cfg_uuid = dictionary.get("uuid", None)

        self.parent = parent

    #####################
    # attributes
    #####################

    def __getattr__(self, item):
        if self.parent:
            return getattr(self.parent, item)
        else:
            raise AttributeError('"%s" not found' % item)

    def _settattr_dict_defaults(self, dictionary, known_attributes):
        """ Set attributes from a dictionary if they are found in the `known_attributes` as known attributes
        """
        for k, v in known_attributes.iteritems():
            if k in dictionary:
                setattr(self, 'cfg_' + k, dictionary[k])

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        if self.name and self.clas:
            assert self.__class__
            return '<%s [name:%s, class:%s] at %x>' % (self.__class__.__name__, self.cfg_name, self.cfg_class, id(self))
        else:
            return '<%s at %x]>' % (id(self))

    def __str__(self):
        return 'name:%s class:%s' % (self.cfg_name, self.cfg_class)
