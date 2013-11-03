#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os

from candelabra.config import config
from candelabra.constants import CFG_BOXES_PATH

logger = getLogger(__name__)


class BoxesStorage(object):
    """ A storage where boxes are stored
    """

    def __init__(self):
        """ Initialize the storage
        """
        super(BoxesStorage, self).__init__()

        self.boxes = {}

        self.path = self.get_storage_root()
        if not os.path.exists(self.path):
            logger.debug('initializing boxes storage from %s', self.path)
            os.makedirs(self.path)

        logger.debug('using boxes storage from %s', self.path)
        self.refresh()

    @staticmethod
    def get_storage_root():
        """ Get the storage root for boxes
        """
        d = config.get_key(CFG_BOXES_PATH)
        return os.path.expandvars(d)

    @staticmethod
    def get_relative_path(path):
        """ Return a path relative to the storage root

        Example:

        >>> get_relative_path("/storage/root/some/box")
        'some/box'
        """
        common = os.path.commonprefix([path, BoxesStorage.get_storage_root()])
        return path[len(common):]

    def get_box(self, name, url):
        """ Get a box instance or make it as missing
        """
        from candelabra.topology.appliance import BoxNode

        if not name in self.boxes:
            new_box = BoxNode(name=name, url=url)
            new_box.missing = True
            self.boxes[name] = new_box
        return self.boxes[name]

    def has_box(self, name):
        """ Return True if the storage has a box with a given name
        """
        return bool(name in self.boxes)

    def refresh(self):
        """ Refresh the list of boxes
        """
        from candelabra.topology.appliance import BoxNode

        self.boxes = {}
        logger.debug('refreshing list of boxes at the storage')
        for entry in os.listdir(self.path):
            fullpath = os.path.abspath(os.path.join(self.path, entry))
            if os.path.isdir(fullpath):
                logger.debug('... checking directory /%s', entry)
                box = BoxNode(name=entry, path=fullpath)
                if box.load():
                    logger.debug('...... box loaded from /%s', entry)
                    self.boxes[entry] = box

        logger.debug('... %d boxes loaded', len(self.boxes))


_boxes_storage = None


def boxes_storage_factory():
    global _boxes_storage
    if not _boxes_storage:
        _boxes_storage = BoxesStorage()
    return _boxes_storage