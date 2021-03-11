# -*- coding: utf-8 -*-
"""
Description:
    This module contains the environment constructs that are used globally for epython.

    NOTE: This module should remain small!

Author:
    Ray Gomez

Date:
    12/7/20
"""
import logging
import os

# Environmental overrides
EPYTHON_LOG_LEVEL = os.getenv("EPYTHON_LOG_LEVEL")
EPYTHON_LOG_FILE = os.getenv("EPYTHON_LOG_FILE")

# Retry overrides
EPYTHON_SSH_RETRIES = os.getenv("EPYTHON_SSH_RETRIES") or 3
EPYTHON_SSH_RETRY_INTERVAL = os.getenv("EPYTHON_SSH_RETRY_INTERVAL") or 5

# SSH Specific
EPYTHON_SSH_KEY = os.getenv("EPYTHON_SSH_KEY")

# Logging overrides
logging.getLogger("paramiko.transport").setLevel(logging.ERROR)


def setup_logging(name="root"):
    """Get the basic root logger."""

    # Define the logging format
    formatter = logging.Formatter('%(asctime)s - [%(pathname)s:%(lineno)d]'
                                  ' - %(levelname)s - %(message)s')

    root = logging.getLogger(name)

    # User provided override for logging
    log_level = logging.INFO
    if EPYTHON_LOG_LEVEL:
        log_level = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warn": logging.WARN,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }.get(EPYTHON_LOG_LEVEL.lower(), None) or log_level

    root.setLevel(log_level)

    # Establish a file to log to
    if EPYTHON_LOG_FILE:
        file_handler = logging.FileHandler(EPYTHON_LOG_FILE, mode="w", encoding=None, delay=False)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # Setup the stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    return root


# This needs to be set after the function is defined
_LOG = setup_logging()
