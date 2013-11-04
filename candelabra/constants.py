#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import sys


################################################
# globals
################################################

DEFAULT_PROVIDER = 'virtualbox'

################################################
# configuration file
################################################

CONFIG_FILE_PATH_CREATION = {
    'darwin': '$HOME/Library/Application Support/Candelabra/candelabra.conf',
    'linux': '$HOME/.candelabra/candelabra.conf',
    'linux2': '$HOME/.candelabra/candelabra.conf',
}

# paths where the config file can be found
CONFIG_FILE_PATHS = [
    CONFIG_FILE_PATH_CREATION[sys.platform],
    '/etc/candelabra/candelabra.conf',
    '/usr/local/etc/candelabra/candelabra.conf',
]

DEFAULT_CFG_SECTION = "candelabra"
DEFAULT_CFG_SECTION_VIRTUALBOX = "candelabra:provider:virtualbox"
DEFAULT_CFG_SECTION_PUPPET = "candelabra:provisioner:puppet"
DEFAULT_CFG_SECTION_DOWNLOADER = "candelabra:downloader"
DEFAULT_CFG_SECTION_LOGGING = "candelabra:logging"
DEFAULT_CFG_SECTION_LOGGING_FILE = "candelabra:logging:file"

################################################
# topology keys
################################################

YAML_ROOT = 'candelabra'
YAML_SECTION_DEFAULT = 'default'
YAML_SECTION_MACHINES = 'machines'
YAML_SECTION_NETWORKS = 'networks'

################################################
# default paths
################################################

DEFAULT_BASE_PATH = {
    'darwin': '$HOME/Library/Application Support/Candelabra/',
    'linux': '$HOME/.candelabra/',
    'linux2': '$HOME/.candelabra/',
}

# default path for the boxes
DEFAULT_BOXES_PATH = {
    'darwin': DEFAULT_BASE_PATH[sys.platform] + 'Boxes/',
    'linux': DEFAULT_BASE_PATH[sys.platform] + 'boxes/',
    'linux2': DEFAULT_BASE_PATH[sys.platform] + 'boxes/',
}

# default logs path
DEFAULT_LOGS_PATH = {
    'darwin': '$HOME/Library/Logs/',
    'linux': DEFAULT_BASE_PATH[sys.platform] + 'logs/',
    'linux2': DEFAULT_BASE_PATH[sys.platform] + 'logs/',
}

DEFAULT_TOPOLOGY_FILE_GUESSES = [
    "candelabra.yaml",
    "candelabra.cfg",
    "candelabra.conf",
    "topology.yaml",
    "topology.cfg",
    "topology.conf",
    "machines.yaml",
    "machines.cfg",
    "machines.conf",
]

DEFAULT_TOPOLOGY_DIR_GUESSES = [
    ".",
    "candelabra",
    "topology",
    ".candelabra",
]

################################################
# configuration keys
################################################

# default provider
CFG_DEFAULT_PROVIDER = (DEFAULT_CFG_SECTION, "default_provider", DEFAULT_PROVIDER)

# boxes path
CFG_BOXES_PATH = (DEFAULT_CFG_SECTION, "boxes_path", DEFAULT_BOXES_PATH[sys.platform])

# log file
CFG_LOG_FILE = (DEFAULT_CFG_SECTION_LOGGING_FILE, "file", DEFAULT_LOGS_PATH[sys.platform] + '/candelabra.log')

# log file level
CFG_LOG_FILE_LEVEL = (DEFAULT_CFG_SECTION_LOGGING_FILE, "level", 'DEBUG')

# log file max size
CFG_LOG_FILE_MAX_LEN = (DEFAULT_CFG_SECTION_LOGGING_FILE, "max_len", 10 * 1024 * 1024)

# bootup until userland session timeout (in seconds)
CFG_USERLAND_TIMEOUT = (DEFAULT_CFG_SECTION, "userland_timeout", 120)

# machine up/down timeout (in seconds)
CFG_MACHINE_UPDOWN_TIMEOUT = (DEFAULT_CFG_SECTION, "updown_timeout", 30)

# machine commands timeout (in seconds)
CFG_MACHINE_COMMANDS_TIMEOUT = (DEFAULT_CFG_SECTION, "commands_timeout", 10)

# download timeout
CFG_DOWNLOAD_TIMEOUT = (DEFAULT_CFG_SECTION_DOWNLOADER, "download_timeout", 120)

# download timeout
CFG_CONNECT_TIMEOUT = (DEFAULT_CFG_SECTION_DOWNLOADER, "connect_timeout", 60)

################################################
# virtualbox
################################################

# paths where VirtualBox can be found
VIRTUALBOX_EXTRA_PATHS = [
    "/Applications/VirtualBox.app",
    "/Applications/VirtualBox.app/Contents/MacOS/",
    "C:\Program Files\Oracle\VirtualBox",
    "/usr/bin",
    "/usr/local/bin",
]

# state file extension
STATE_FILE_EXTENSION = 'state'

################################################
# logging
################################################

LOG_CONSOLE_FORMAT = "%(log_color)s[%(asctime)-15s | %(levelname)-8s]  %(message)-80s"
LOG_CONSOLE_FORMAT_DEBUG = LOG_CONSOLE_FORMAT + " [%(filename)s/%(funcName)s():%(lineno)d]"

LOG_FILE_FORMAT = "[%(asctime)-15s | %(levelname)-8s]  %(message)-80s"
LOG_FILE_FORMAT_DEBUG = LOG_FILE_FORMAT + " [%(filename)s/%(funcName)s():%(lineno)d]"
