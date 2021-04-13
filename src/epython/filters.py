# -*- coding: utf-8 -*-
"""
Description:
    This module contains all types of filters useful for QA

Author:
    Ray Gomez

Date:
    3/22/21
"""

import os
import re

from epython import errors
from epython.environment import _LOG


def generic_log_filter(logfile, start, end, inplace=True, outfile=None):
    """ Sanitize a log to only include relevant pieces for an individual test.

    Args:
        logfile (str): The path to the logfile to process
        start (str): String pattern to match on to determine the start of a log file
        end (str): String pattern to match on to determine the end of a log file
        inplace (bool): Whether or not the filtering should be done inplace
        outfile (str): The file to save the filtered log as
    """

    if not os.path.exists(logfile):
        errors.filters.EFilterException(f"Failed finding {logfile} to process")

    if not inplace and not outfile:
        errors.filters.EFilterException("Non inplace saving requires specifying an output file")

    capturing = False
    processed_file = ""
    with open(logfile) as _file:
        _LOG.info(f"Processing file {logfile}")
        for line in _file:

            # Find the start position
            if start in line:
                capturing = True

            # Capture the log line if we are within the capturing state
            if capturing:
                processed_file += line

            # Find the end position
            if capturing and end in line:
                break
        else:
            _LOG.info(f"End of {logfile} not found, capturing everything past start position.")

    # Don't overwrite file if nothing was found
    if not processed_file:
        _LOG.info("Couldn't find start/end for logfile, skipping processing.")
        return

    # Overwrite the existing file
    _outfile = logfile
    if not inplace:
        _LOG.info(f"Saving filtered {logfile} to {_outfile}")
        _outfile = outfile

    with open(_outfile, "w") as text_file:
        text_file.write(processed_file)


def regex_log_filter(logfile, start, end, inplace=True, outfile=None):
    """ Similar to the generic_log_filter but using regex instead of string start/end filters

    Args:
        logfile (str): The path to the logfile to process
        start (re.Pattern): Compiled regex pattern to match on to determine the start of a log file
        end (re.Pattern): Compiled regex pattern to match on to determine the end of a log file
        inplace (bool): Whether or not the filtering should be done inplace
        outfile (str): The file to save the filtered log as
    """

    if not os.path.exists(logfile):
        errors.filters.EFilterException(f"Failed finding {logfile} to process")

    if not inplace and not outfile:
        errors.filters.EFilterException("Non inplace saving requires specifying an output file")

    if not isinstance(start, re.Pattern) or not isinstance(end, re.Pattern):
        errors.filters.ERegExFilterException("The start and end variables must be of type re.Pattern")


    capturing = False
    processed_file = ""
    with open(logfile) as _file:
        _LOG.info(f"Processing file {logfile}")
        for line in _file:

            # Find the start position
            if start in line:
                capturing = True

            # Capture the log line if we are within the capturing state
            if capturing:
                processed_file += line

            # Find the end position
            if capturing and end in line:
                break
        else:
            _LOG.info(f"End of {logfile} not found, capturing everything past start position.")

    # Don't overwrite file if nothing was found
    if not processed_file:
        _LOG.info("Couldn't find start/end for logfile, skipping processing.")
        return

    # Overwrite the existing file
    _outfile = logfile
    if not inplace:
        _LOG.info(f"Saving filtered {logfile} to {_outfile}")
        _outfile = outfile

    with open(_outfile, "w") as text_file:
        text_file.write(processed_file)
