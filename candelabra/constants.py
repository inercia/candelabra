#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

COMMANDS_BASE = ['candelabra', 'command']
PROVIDER_BASE = ['candelabra', 'provider']

YAML_ROOT = 'candelabra'
YAML_SECTION_DEFAULT = 'default'
YAML_SECTION_MACHINES = 'machines'
YAML_SECTION_NETWORKS = 'networks'

# default supported commands
DEFAULT_COMMANDS = ['up', 'provision', 'import', 'show']

# paths where the config file can be found
CONFIG_FILE_PATHS = [
    '$HOME/Library/Preferences/candelabra.conf',
    '/etc/candelabra/candelabra.conf',
    '/usr/local/etc/candelabra/candelabra.conf',
]

DEFAULT_CFG_SECTION_VIRTUALBOX = "candelabra:provider:virtualbox"
DEFAULT_CFG_SECTION_PUPPET = "candelabra:provisioner:puppet"

CONFIG_FILE_PATH_CREATION = {
    'darwin': '$HOME/Library/Application Support/Candelabra/candelabra.conf',
}

DEFAULT_STORAGE_PATH = {
    'darwin': '$HOME/Library/Application Support/Candelabra/Storage/',
}

# paths where VirtualBox can be found
VIRTUALBOX_EXTRA_PATHS = [
    "/Applications/VirtualBox.app",
    "/Applications/VirtualBox.app/Contents/MacOS/",
    "C:\Program Files\Oracle\VirtualBox",
    "/usr/bin",
    "/usr/local/bin",
]
