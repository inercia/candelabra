#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import tarfile
import tempfile
import json

from candelabra.config import config
from candelabra.constants import DEFAULT_PROVIDERS, CFG_BOXES_PATH, CFG_CONNECT_TIMEOUT, CFG_DOWNLOAD_TIMEOUT
from candelabra.errors import UnsupportedBoxException, ImportException
from candelabra.loader import load_provider_box_for

logger = getLogger(__name__)

#: a mbyte
MBYTE = 1024 * 1024


class Box(object):
    """ A box is one or more virtual machine templates that will be used for creating multiple virtual machines
    following a topology.

    Boxes contain subdirectories for providers, where appliances are stored.

    Example: box1 has two appliances: a virtualbox appliance and a vmware appliance

    - box1
      - virtualbox
        - box.ovf
        - disk.vmdk
      - vmware
        - ...
    """

    def __init__(self, name, path=None, url=None, missing=False):
        """ Initialize a box
        :param name: the box name (ie, 'centos-6.4')
        :param path: (optional) the box full path
        :param url: (optional) the origin URL
        """
        self.name = name
        self.path = path if path else os.path.join(BoxesStorage.get_storage_root(), name)
        self.url = url
        self.appliances = {}
        self.missing = missing

        if not os.path.exists(self.path):
            logger.debug('creating box directory "%s"', self.path)
            os.makedirs(self.path)

    def load(self):
        """ Load a box from a path
        """
        logger.debug('... searching for providers in box %s', self.name)
        self.appliances.clear()
        for provider in os.listdir(self.path):
            if provider in set(DEFAULT_PROVIDERS):
                logger.debug('...... found a %s template', provider)
                box_class = load_provider_box_for(provider)
                full_provider_path = os.path.abspath(os.path.join(self.path, provider))

                # try to load the provider
                try:
                    box_provider = box_class.from_dir(full_provider_path)
                except UnsupportedBoxException, e:
                    logger.warning('...... not a valid %s template in %s', provider, full_provider_path)
                else:
                    self.appliances[provider] = box_provider

        return bool(len(self.appliances) > 0)

    def get_tasks_import(self):
        """ Returns all the tasks needed for importing this box
        """
        res = []
        for provider in self.appliances:
            res += provider.get_tasks_import()
        return res

    def get_appliance(self, provider):
        """ Get a instance of one of the appliances in this box
        :raise KeyError: if no appliance found
        """
        return self.appliances[provider]

    #####################
    # tasks
    #####################

    def do_download(self):
        """ Download a box
        """
        if self.missing:
            if self.url is None:
                raise ImportException('input URL not specified')

            import pycurl

            logger.info('downloading image from "%s"', self.url)

            curl = pycurl.Curl()
            temp_box_fp, temp_box_name = tempfile.mkstemp()
            try:
                temp_box_file = os.fdopen(temp_box_fp, 'w+')
                logger.info('... downloading to temporal file "%s"', temp_box_name)

                self.downloaded_mbytes = 0

                def cb_progress(download_t, download_d, upload_t, upload_d):
                    dmbytes = int(download_d / MBYTE)
                    if dmbytes > self.downloaded_mbytes:
                        logger.debug('downloaded=%d Mb, total=%d Mbytes', dmbytes, download_t / MBYTE)
                        self.downloaded_mbytes = dmbytes

                curl.setopt(pycurl.URL, str(self.url))
                curl.setopt(pycurl.WRITEFUNCTION, temp_box_file.write)
                curl.setopt(curl.NOPROGRESS, 0)
                curl.setopt(curl.PROGRESSFUNCTION, cb_progress)
                curl.setopt(pycurl.CONNECTTIMEOUT, config.get_key(CFG_CONNECT_TIMEOUT))
                curl.setopt(pycurl.TIMEOUT, config.get_key(CFG_DOWNLOAD_TIMEOUT))
                curl.setopt(pycurl.FOLLOWLOCATION, 1)
                curl.perform()
            except KeyboardInterrupt:
                logger.debug('... removing %s', temp_box_name)
                os.remove(temp_box_name)
                raise ImportException('could not perform download')
            except Exception, e:
                logger.critical('while downloading: %s', str(e))
                logger.debug('... removing %s', temp_box_name)
                os.remove(temp_box_name)
                raise ImportException('could not perform download')
            finally:
                curl.close()
                temp_box_file.close()

            logger.info('downloaded %d bytes!', self.downloaded_mbytes)
            self.missing = False

            appliance_path = os.path.join(self.path, 'unknown')
            if not os.path.exists(appliance_path):
                logger.debug('creating unknown appliance directory "%s"', appliance_path)
                os.makedirs(appliance_path)

            try:
                logger.info('extracting box...')
                tar = tarfile.open(temp_box_name)
                tar.extractall(path=appliance_path)
                tar.close()
                logger.debug('... done')
            except IOError, e:
                logger.info('error extracting box: %s', str(e))
            finally:
                logger.debug('removing temporal file...')
                os.remove(temp_box_name)

            metadata_file_path = os.path.join(appliance_path, 'metadata.json')
            if os.path.isfile(metadata_file_path):
                with open(metadata_file_path, 'r') as metadata_file:
                    metadata = json.load(metadata_file)
                    provider = metadata["provider"]

                    logger.debug('renaming appliance to "%s"', provider)
                    fixed_appliance_path = os.path.join(self.path, provider)
                    os.rename(appliance_path, fixed_appliance_path)

    #####################
    # auxiliary
    #####################

    def __repr__(self):
        """ The representation
        """
        return "<Box %s appliances=%s %s at 0x%x>" % (self.name,
                                                      self.appliances, '[missing]' if self.missing else '[present]',
                                                      id(self))


########################################################################################################################

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
        if not name in self.boxes:
            self.boxes[name] = Box(name=name, url=url, missing=True)
        return self.boxes[name]

    def has_box(self, name):
        """ Return True if the storage has a box with a given name
        """
        return bool(name in self.boxes)

    def refresh(self):
        """ Refresh the list of boxes
        """
        self.boxes = {}
        logger.debug('refreshing list of boxes at the storage')
        for entry in os.listdir(self.path):
            fullpath = os.path.abspath(os.path.join(self.path, entry))
            if os.path.isdir(fullpath):
                logger.debug('... checking directory /%s', entry)
                box = Box(name=entry, path=fullpath)
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