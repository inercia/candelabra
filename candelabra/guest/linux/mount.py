
# First mount command uses getent to get the group
mount_options = "-o uid=`id -u #{options[:owner]}`,gid=`getent group #{options[:group]} | cut -d: -f3`"
mount_options += ",#{options[:mount_options].join(",")}" if options[mount_options] else ''
mount_commands = "mount -t vboxsf #{mount_options} #{name} #{expanded_guest_path}"

# Second mount command uses the old style `id -g`
mount_options = "-o uid=`id -u #{options[:owner]}`,gid=`id -g #{options[:group]}`"
mount_options += ",#{options[:mount_options].join(",")}" if options[mount_options] else ''
mount_commands = "mount -t vboxsf #{mount_options} #{name} #{expanded_guest_path}"