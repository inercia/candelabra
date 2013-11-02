#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import os
from logging import getLogger
import tempfile
import tarfile
import json

from candelabra.tasks import TaskGenerator
from candelabra.errors import UnsupportedBoxException, ImportException
from candelabra.plugins import PLUGINS_REGISTRIES
from candelabra.config import config
from candelabra.constants import CFG_CONNECT_TIMEOUT, CFG_DOWNLOAD_TIMEOUT
from candelabra.topology.node import TopologyNode

logger = getLogger(__name__)

#: a mbyte
MBYTE = 1024 * 1024


class Box(TopologyNode, TaskGenerator):
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

    # known attributes
    # the right value is either:
    # - a constructor
    # - tuple is the constructor and a default value (None means "inherited from parent")
    __known_attributes = {
        'name': (str, ''),
        'path': (str, ''),
        'url': (str, ''),
    }

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(Box, self).__init__(_parent=_parent, **kwargs)
        self._settattr_dict_defaults(kwargs, self.__known_attributes)

        self.appliances = {}

        self.path = getattr(self, 'cfg_path', None)
        if not self.path:
            from candelabra.boxes import BoxesStorage
            self.path = os.path.join(BoxesStorage.get_storage_root(), self.cfg_name)

        if not os.path.exists(self.path):
            logger.debug('creating box directory "%s"', self.path)
            os.makedirs(self.path)
            self.missing = True
        else:
            self.missing = False

    def load(self):
        """ Load a box from a path
        """
        supported_providers_names = PLUGINS_REGISTRIES['candelabra.provider'].names

        logger.debug('... searching for providers in box %s', self.cfg_name)
        self.appliances.clear()
        for provider in os.listdir(self.path):
            if provider in set(supported_providers_names):
                logger.debug('...... found a %s template', provider)

                providers = PLUGINS_REGISTRIES['candelabra.provider']
                provider_plugin = providers[provider]
                appliance_class = provider_plugin.APPLIANCE

                full_provider_path = os.path.abspath(os.path.join(self.path, provider))

                # try to load the appliance provider for this box class (ie, 'VirtualboxAppliance')
                try:
                    appliance_instance = appliance_class.from_dir(full_provider_path)
                except UnsupportedBoxException, e:
                    logger.warning('...... not a valid %s template in %s', provider, full_provider_path)
                else:
                    self.appliances[provider] = appliance_instance

        return bool(len(self.appliances) > 0)

    def get_appliance(self, provider):
        """ Get a instance of one of the appliances in this box, or None if not found
        """
        if len(self.appliances) == 0:
            self.load()

        try:
            # returns the provider (ie, a 'VirtualboxAppliance' instance)
            return self.appliances[provider]
        except KeyError:
            return None

    #####################
    # tasks
    #####################

    def do_download(self):
        """ Download a box
        """
        if self.missing:
            if not self.cfg_url:
                raise ImportException('input URL not specified (url="%s")' % str(self.cfg_url))

            logger.info('downloading image from "%s"', self.cfg_url)

            try:
                temp_box_fp, temp_box_name = tempfile.mkstemp()
                temp_box_file = os.fdopen(temp_box_fp, 'w+')
            except IOError, e:
                raise ImportException('could not create temporal file for download: %s' % str(e))

            try:
                import pycurl
                curl = pycurl.Curl()
                logger.info('... downloading to temporal file "%s"', temp_box_name)

                self.downloaded_mbytes = 0

                def cb_progress(download_t, download_d, upload_t, upload_d):
                    dmbytes = int(download_d / MBYTE)
                    if dmbytes > self.downloaded_mbytes:
                        logger.debug('downloaded=%d Mb, total=%d Mbytes', dmbytes, download_t / MBYTE)
                        self.downloaded_mbytes = dmbytes

                curl.setopt(pycurl.URL, str(self.cfg_url))
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
        return "<Box %s appliances=%s %s at 0x%x>" % (self.cfg_name,
                                                      self.appliances, '[missing]' if self.missing else '[present]',
                                                      id(self))

