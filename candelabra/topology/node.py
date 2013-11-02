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

    # known attributes
    # the right tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = {
        'name': (str, ''),
        'class': (str, ''),
        'uuid': (str, ''),
    }

    __state_attributes = {
        'name',
        'class',
        'uuid',
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        self._settattr_dict_defaults(kwargs, self.__known_attributes)
        self._parent = _parent

    #####################
    # attributes
    #####################

    def __getattr__(self, item):
        if self._parent:
            return getattr(self._parent, item)
        else:
            if item.startswith('cfg_'):
                return None
            else:
                raise AttributeError('"%s" not found' % item)

    def _settattr_dict_defaults(self, dictionary, known_attributes):
        """ Set attributes from a dictionary if they are found in the `known_attributes` as known attributes
        """
        def recursive_builder(value, constructor):
            if isinstance(value, (list, tuple)):
                constructed_value = [recursive_builder(value_item, constructor) for value_item in value]
            elif isinstance(value, dict):
                constructed_value = constructor(**value)
            else:
                constructed_value = constructor(value)
            return constructed_value

        _unset = object()
        for attr, attr_props in known_attributes.iteritems():
            constructor, default = attr_props if isinstance(attr_props, tuple) else (attr_props, _unset)
            if attr in dictionary:
                value = dictionary[attr]
                if constructor:
                    constructed_value = recursive_builder(value, constructor)
                else:
                    constructed_value = default
                setattr(self, 'cfg_' + attr, constructed_value)
            elif default is not _unset:
                setattr(self, 'cfg_' + attr, default)
            else:
                # do not try to set the default value if it was not set
                # so __getattr__ will be invoked and we will look for the value in the parent object
                pass

    def get_state_dict(self):
        """ Get current state as a dictionary, suitable for saving in a state file
        """
        local_dict = {}
        try:
            for attr in self.__state_attributes:
                v = getattr(self, 'cfg_' + attr, None)
                if v:
                    local_dict[attr] = v
        except AttributeError:
            pass
        return local_dict

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        if self.cfg_name and self.cfg_class:
            return '<%s [name:%s, class:%s] at %x>' % (self.__class__.__name__,
                                                       self.cfg_name,
                                                       self.cfg_class,
                                                       id(self))
        else:
            return '<%s at %x]>' % (id(self))

    def __str__(self):
        return 'name:%s class:%s' % (self.cfg_name, self.cfg_class)
