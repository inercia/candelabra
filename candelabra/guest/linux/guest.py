#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Linux guest definition
"""

from logging import getLogger

from candelabra.base import Guest

logger = getLogger(__name__)

#: create a directory if it does not exist
MKDIR_COMMAND = "mkdir {directory}"
#: the command used for mounting a shared folder in a Linux machine
MOUNT_COMMAND = "mount -t {type} {mount_options} {directory} {mount_point}"
MOUNT_OPTIONS = "-o uid=`id -u {owner}`,gid=`getent group {group} | cut -d: -f3`"

#: the command used for shutting down a Linux machine
SHUTDOWN_COMMAND = "shutdown -h now"


class LinuxGuest(Guest):
    """ A Linux guest
    """

    def mkdir(self, directory):
        """ Create a remote directory
        """
        mkdir_command = MKDIR_COMMAND.format(directory=directory).split(' ')
        return self.communicator.sudo(mkdir_command)

    def mount(self, directory, mount_point, type='vboxsf', owner='vagrant', group='vagrant'):
        """ Mount a directory on a mount point
        """
        logger.info('mounting %s', directory)
        mount_options = MOUNT_OPTIONS.format(owner=owner, group=group)
        mount_command = MOUNT_COMMAND.format(directory=directory, type=type, mount_point=mount_point,
                                             mount_options=mount_options).split(' ')
        return self.communicator.sudo(mount_command)

    def shutdown(self):
        """ Shutdown the machine
        """
        shutdown_command = SHUTDOWN_COMMAND.split(' ')
        return self.communicator.sudo(shutdown_command)


