#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
A base module for all the topology nodes.
"""

from copy import copy
from logging import getLogger
from candelabra.tasks import TaskGenerator

logger = getLogger(__name__)

_unset = object()


class TopologyAttribute(object):
    """ A topology node attribute

    Nodes have some important attributes:

    * a **class** that identifies what kind of node is this
    * a unique **name**
    * a unique **uuid**, usually established by the Candelabra engine.
    """

    def __init__(self, constructor, default=_unset, doc='', inherited=False, copy=False, append=False):
        """
        Initialize a topology node attribute

        Topology node attributes are built by invoking a :param:`constructor` with the
        dictionary of elements in the YAML file. If no values are found, a default value can be
        set with the :param:`default` parameter.

        For nodes with a `_parent` attribute, the value can be inherited from the parent if the
        :param:`inhertited` value is set. In this case, both parent and child will refer to the
        same variable instance, so a change in one of them will be seen in the other.

        :param inherited: the attribute is kept as a link to the value in the parent, so if the value changes in
                          the parent, it does so in this instance
        :param copy: the attribute is copied from the parent
        """
        assert (copy or inherited) and (copy != inherited), 'both parameters are exclusive'
        self.constructor = constructor
        self.default = default
        self.inherited = inherited
        self.copy = copy
        self.doc = doc
        self.append = append

    @staticmethod
    def setall(container, dictionary, known_attributes):
        """ Set attributes from a dictionary if they are found in the `known_attributes` as known attributes.

        We can define all attributed this kind of object accept with the :param:`known_attributes`
        For constructor, we pass the dictionary expanded as parameters, and we add a `_parent_contructor`
        for referring to this instance.
        """

        def recursive_builder(value, constructor):
            if isinstance(value, (list, tuple)):
                constructed_value = [recursive_builder(value_item, constructor) for value_item in value]
            elif isinstance(value, dict):
                constructed_value = constructor(_container=container, **value)
            else:
                constructed_value = constructor(value)
            return constructed_value

        def copy_builder(value, container, attr_name):
            v = copy(value)
            if hasattr(v, '_container'):
                v._container = container
            return v

        for attr_name, attr_instance in known_attributes.iteritems():
            assert isinstance(attr_instance, TopologyAttribute)
            if attr_name in dictionary:
                value = dictionary[attr_name]
                if attr_instance.constructor:
                    constructed_value = recursive_builder(value, attr_instance.constructor)
                    if attr_instance.append:
                        constructed_value = getattr(container, 'cfg_' + attr_name) + constructed_value
                else:
                    constructed_value = attr_instance.default
                setattr(container, 'cfg_' + attr_name, constructed_value)

            elif attr_instance.copy and container._parent:
                parent_value = getattr(container._parent, 'cfg_' + attr_name, _unset)
                if parent_value is not _unset:
                    if isinstance(parent_value, (list, tuple)):
                        res = [copy_builder(v, container, attr_name) for v in parent_value]
                    else:
                        res = copy_builder(parent_value, container, attr_name)

                    setattr(container, 'cfg_' + attr_name, res)

                elif attr_instance.default is not _unset:
                    setattr(container, 'cfg_' + attr_name, attr_instance.default)

            elif attr_instance.default is not _unset:
                setattr(container, 'cfg_' + attr_name, attr_instance.default)
            else:
                assert attr_instance.inherited
                assert attr_instance.default is _unset
                # do not try to set the default value if it was not set
                # so __getattr__ will be invoked and we will look for the value in the parent object


######################################################################################################################

class TopologyNode(TaskGenerator):
    """ Base class for all topology nodes.

    *Attributes:*

    All known attributed will be loaded from the topology wile and added to the current instance with
    the 'cfg_' prefix. For example, if 'hostname' is a known attribute, it will be set for the
    instance under the name 'cfg_hostname'

    *Commands:*

    Topology nodes can react to commands by providing methods named `get_tasks_<COMMAND>` that return a list
    of tuples (function1, function2)
    """

    # known attributes
    # the right tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = {
        'name': TopologyAttribute(constructor=str, default='', inherited=True),
        'class': TopologyAttribute(constructor=str, default=None, inherited=True),
        'uuid': TopologyAttribute(constructor=str, default='', copy=True),
    }

    __state_attributes = {
        'name',
        'class',
        'uuid',
    }

    def __init__(self, **kwargs):
        """ Initialize a topology node, building all the attributes by merging the dictionary given
        in the keyword arguments and the `__known_attributes` parameter
        """
        super(TopologyNode, self).__init__()
        self._parent = kwargs.pop('_parent', None)
        self._container = kwargs.pop('_container', None)

        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

    #####################
    # attributes
    #####################

    def __getattr__(self, item):
        if item.startswith('cfg_') and self._parent:
            return getattr(self._parent, item, None)
        raise AttributeError('"%s" not found' % item)

    def get_state_dict(self):
        """ Get current state as a dictionary, suitable for saving in a state file
        """
        local_dict = {}
        try:
            for attr in self.__state_attributes:
                v = getattr(self, 'cfg_' + attr, None)
                if v:
                    if hasattr(v, 'get_state_dict'):
                        local_dict[attr] = v.get_state_dict()
                    else:
                        local_dict[attr] = v
        except AttributeError:
            pass
        return local_dict

    is_global = property(lambda self: self._parent is None, doc='True if this is the global node')

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        extra = []
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_class:
            extra += ['class:%s' % self.cfg_class]

        return "<%s(%s) at 0x%x>" % (self.__class__.__name__, ','.join(extra), id(self))


