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
from candelabra.topology.node import TopologyNode, TopologyAttribute

logger = getLogger(__name__)

#: a mbyte
MBYTE = 1024 * 1024

#: download chunk size
CHUNK_SIZE = 4 * MBYTE


class BoxNode(TopologyNode, TaskGenerator):
    """ A box is one or more virtual machine templates that will be used for creating
    multiple virtual machines following a topology.

    Boxes contain subdirectories for providers, where appliances are stored.

    Example: box1 has two appliances: a virtualbox appliance and a vmware appliance

.. code-block:: yaml

            - box1
              - virtualbox
                - box.ovf
                - disk.vmdk
              - vmware
                - ...

    """

    __known_attributes = [
        TopologyAttribute('name', str, default='', inherited=True),
        TopologyAttribute('path', str, default='', inherited=True),
        TopologyAttribute('url', str, default='', inherited=True),
        TopologyAttribute('username', str, default='vagrant', inherited=True),
        TopologyAttribute('password', str, default='password', inherited=True),
        TopologyAttribute('sudo_command', str, default='/usr/bin/sudo', inherited=True),
        TopologyAttribute('ifconfig_command', str, default='/sbin/ifconfig', inherited=True),
    ]

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(BoxNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self.__known_attributes)

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

                providers_registry = PLUGINS_REGISTRIES['candelabra.provider']
                provider_plugin = providers_registry.plugins[provider]
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
                logger.info('... downloading to temporal file "%s"', temp_box_name)

                import requests

                downloaded_bytes = 0
                last_downloaded_mbytes = 0
                r = requests.get(self.cfg_url, stream=True)
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:                           # filter out keep-alive new chunks
                        downloaded_bytes += temp_box_file.write(chunk)
                        downloaded_mbytes = int(downloaded_bytes / MBYTE)
                        if downloaded_mbytes > last_downloaded_mbytes:
                            logger.debug('downloaded=%d Mb', downloaded_mbytes)
                            last_downloaded_mbytes = downloaded_mbytes

                        temp_box_file.flush()

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
                temp_box_file.close()

            logger.info('downloaded %d bytes!', self.downloaded_mbytes)
            self.missing = False

            appliance_path = os.path.join(self.path, 'unknown')
            if not os.path.exists(appliance_path):
                logger.debug('creating unknown box directory "%s"', appliance_path)
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

                    logger.debug('renaming box to "%s"', provider)
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

