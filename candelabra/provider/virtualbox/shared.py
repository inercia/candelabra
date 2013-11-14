#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os

import virtualbox as _virtualbox
from candelabra.topology.node import TopologyAttribute

from candelabra.topology.shared import SharedNode


logger = getLogger(__name__)


class VirtualboxSharedNode(SharedNode):
    """ A VirtualBox shared folder for a machine
    """

    def __init__(self, _parent=None, **kwargs):
        """ Initialize a topology node
        """
        super(SharedNode, self).__init__(_parent=_parent, **kwargs)
        TopologyAttribute.setall(self, kwargs, self._SharedNode__known_attributes)

        from candelabra.provider.virtualbox import VirtualboxMachineNode

        assert self._container is not None and isinstance(self._container, VirtualboxMachineNode)

        self.installed = False

    @property
    def machine(self):
        return self._container

    #####################
    # tasks
    #####################

    def do_shared_create(self):
        """ Share the folders
        """
        assert not self.machine.is_global

        s = self.machine.lock()
        try:
            local_path = os.path.abspath(os.path.expandvars(self.cfg_local))
            remote_path = self.cfg_remote

            # update the paths, so they are left for the "mount" action
            self.cfg_local = local_path
            self.cfg_remote = remote_path

            if not os.path.exists(local_path):
                logger.warning('... local folder %s does not exist! skipping...', local_path)
            elif not os.path.isdir(local_path):
                logger.warning('... local folder %s is not a directory! skipping...', local_path)
            else:
                logger.info('creating shared folder: %s -> %s', local_path, remote_path)
                try:
                    s.console.create_shared_folder(remote_path,
                                                   local_path,
                                                   writable=self.cfg_writable,
                                                   automount=False)
                except _virtualbox.library.VBoxErrorFileError:
                    pass
                else:
                    self.installed = True

        except _virtualbox.library.VBoxError, e:
            logger.warning(str(e))
        finally:
            self.machine.unlock(s)

    def do_shared_mount(self):
        """ Mount the folders
        """
        if self.installed:
            # s = self.machine.lock()
            try:
                # guest_session = self.machine.get_guest_session(s)

                logger.info('starting shared folder "%s"...', self.cfg_remote)

                if self.cfg_create_if_missing:
                    logger.debug('... creating directory %s', self.cfg_remote)
                    code, stdout, stderr = self.machine.guest.mkdir(self.cfg_remote)
                    for line in stdout.splitlines():
                        logger.debug('... output: %s', line)

                # when mounting the remote, the directory is identifies _only_ by the remote name
                code, stdout, stderr = self.machine.guest.mount(self.cfg_remote, self.cfg_remote, type='vboxsf',
                                                                owner=self.cfg_owner, group=self.cfg_group)
                for line in stdout.splitlines():
                    logger.debug('... output: %s', line)

                logger.debug('... done')

            except _virtualbox.library.VBoxError, e:
                logger.warning(str(e))
            finally:
                #self.machine.unlock(s)
                pass


    #####################
    # auxiliary
    #####################
    def __repr__(self):
        """ The representation
        """
        extra = []
        if self.cfg_name:
            extra += ['name:%s' % self.cfg_name]
        if self.cfg_uuid:
            extra += ['uuid:%s' % self.cfg_uuid]
        if self.cfg_local:
            extra += ['local:%s' % self.cfg_local]
        if self.cfg_remote:
            extra += ['remote:%s' % self.cfg_remote]

        return "<VirtualboxShared(%s) at 0x%x>" % (','.join(extra), id(self))
