#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#
"""
Commands must define, in the __init__ file:
- a DESCRIPTION
- a argparser() function
- a run() function
"""

import sys
import logging
import logging.handlers
from colorlog import ColoredFormatter

from candelabra.constants import LOG_CONSOLE_FORMAT_DEBUG, LOG_CONSOLE_FORMAT, LOG_FILE_FORMAT_DEBUG, LOG_FILE_FORMAT, DEFAULT_CFG_SECTION_LOGGING_FILE, CFG_LOG_FILE, CFG_LOG_FILE_LEVEL, CFG_LOG_FILE_MAX_LEN

# supported log levels
LOGLEVELS = [l for l in logging._levelNames if isinstance(l, basestring)]


def setup_console(level=logging.INFO, date_format=None):
    """ Setup the logging in console
    """
    log_format_console = LOG_CONSOLE_FORMAT_DEBUG if level == 'DEBUG' else LOG_CONSOLE_FORMAT

    # example format:
    # "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s"

    # add the console
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter(
        log_format_console,
        datefmt=None,
        reset=True,
    )
    hdlr.setFormatter(formatter)
    hdlr.setLevel(level)
    logging.root.addHandler(hdlr)

    logging.root.setLevel(logging.DEBUG)


def setup_file(filename=None, level=None):
    """ Add a logging file to the logging configuration

    If no filename is given, we will check the config file for a valid logfile configuration.
    If not found, no logging to file is configured.
    """
    from candelabra.config import config

    if not filename:
        if config.has_section(DEFAULT_CFG_SECTION_LOGGING_FILE):
            filename = config.get_key(CFG_LOG_FILE)
        else:
            filename = None

    if filename:
        if not level:
            if config.has_section(DEFAULT_CFG_SECTION_LOGGING_FILE):
                level = config.get_key(CFG_LOG_FILE_LEVEL)

        max_log_size = long(config.get_key(CFG_LOG_FILE_MAX_LEN))
        log_format_file = LOG_FILE_FORMAT_DEBUG if level == 'DEBUG' else LOG_FILE_FORMAT

        # add the file
        try:
            hdlr = logging.handlers.RotatingFileHandler(str(filename), maxBytes=max_log_size, backupCount=1)
        except IOError, e:
            logging.critical('cannot create log file: %s', str(e))
            sys.exit(1)

        fmt = logging.Formatter(log_format_file, None)
        hdlr.setFormatter(fmt)
        hdlr.setLevel(level)
        logging.root.addHandler(hdlr)
