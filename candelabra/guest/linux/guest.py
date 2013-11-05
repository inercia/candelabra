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

#: command for getting the IP addresses
GET_IPS_COMMAND = "ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1 }'"


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

    def get_ips(self):
        """ Get the IP addresses
        """
        command = GET_IPS_COMMAND.split(' ')
        return self.communicator.sudo(command)

    def change_hostname(self, name):
        # Get the current hostname
        # if existing fqdn setup improperly, this returns just hostname
        old = ''
        command = "hostname -f"
        code, stdout, stderr = self.communicator.sudo(command)
        if len(stdout):
            old = stdout

        # this works even if they're not both fqdn
        old_1 = old.split('.')[0]
        name_1 = name.split('.')[0]
        if old_1 != name_1:

            self.communicator.sudo("sed -i 's/.*$/{name_1}/' /etc/hostname".format(name_1=name_1))

            # hosts should resemble:
            # 127.0.0.1   localhost host.fqdn.com host
            # 127.0.1.1   host.fqdn.com host
            self.communicator.sudo(
                "sed -ri 's@^(([0-9]{1,3}\.){3}[0-9]{1,3})\\s+(localhost)\\b.*$@\\1\\t{name} {name_1} \\3@g' /etc/hosts".format(
                    name=name,
                    name_1=name_1))

            self.communicator.sudo(
                "sed -ri 's@^(([0-9]{1,3}\.){3}[0-9]{1,3})\\s+({old_1})\\b.*$@\\1\\t{name} {name_1}@g' /etc/hosts".format(
                    old_1=old_1,
                    name=name,
                    name_1=name_1))

            if self.communicator.test("`lsb_release -c -s` = hardy"):
            # hostname.sh returns 1, so I grep for the right name in /etc/hostname just to have a 0 exitcode
                self.communicator.sudo(("/etc/init.d/hostname.sh start; grep '{name}' /etc/hostname".format(name=name)))

            else:
                self.communicator.sudo("service hostname start")

            self.communicator.sudo("hostname --fqdn > /etc/mailname")
            self.communicator.sudo("ifdown -a; ifup -a; ifup -a --allow=hotplug")

