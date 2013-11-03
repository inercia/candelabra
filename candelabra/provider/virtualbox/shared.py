#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
from time import sleep

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
        return self._container.get_machine()

    def do_install(self):
        """ Share the folders
        """
        assert not self._container.is_global

        s = self.machine.create_session()
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
                logger.info('shared folder: %s -> %s', local_path, remote_path)
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
            s.unlock_machine()

    def do_mount(self):
        """ Mount the folders
        """
        if self.installed:
            s = _virtualbox.Session()
            try:
                self.machine.lock_machine(s, _virtualbox.library.LockType.shared)
                sleep(1.0)
                # guest = s.console.guest.create_session('vagrant', 'vagrant')

                remote_path = self.cfg_remote

                logger.info('mounting shared folders')
                # assert self._guest_session is not None
                #logger.info('... mounting %s', remote_path)
                #try:
                #    self._guest_session.directory_create(remote_path, 755,
                #                                         [_virtualbox.library.DirectoryCreateFlag.parents])
                #except _virtualbox.library.VBoxErrorFileError:
                #    pass

                logger.info('shared folders configured.')
            except _virtualbox.library.VBoxError, e:
                logger.warning(str(e))
            finally:
                s.unlock_machine()

    #####################
    # auxiliary
    #####################

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
