# -*- coding: utf-8 -*-
"""
Description:
    Test epython filters

Author:
    Ray

Date:
    4/15/21
"""

import os
import pathlib
import random
import tempfile

import pytest

from epython.environment import _LOG
from epython import errors, filters

TEST_PATH = pathlib.Path(__file__).parent.absolute()
RESOURCES_PATH = f"{TEST_PATH}/resources"

# Test specifics

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
START_TEST = "Bogus Test Start!!\n"
END_TEST = "Bogus Test End!!\n"


def generate_logfile(outfile, start=START_TEST, end=END_TEST, log_msg=LOREM_IPSUM, random_count=True):

    random_count = random.randint(0, 100)
    _LOG.info(f"Creating a log file with {random_count} log entries.")

    output = f"{START_TEST}"
    for i in range(0, random_count):
        output += f"{LOREM_IPSUM}"
    output += f"{END_TEST}"

    with open(outfile, "w+") as f:
        _LOG.info(f"Writing generated log content to {outfile}")
        f.write(output)

    return random_count


@pytest.mark.wip
@pytest.mark.L1
def test_happy_path_generic_log_filter():
    """ Test to make sure the generic log filter is working as expected. """

    original_logfile = "/tmp/pytest_unfiltered.log"
    filtered_logfile = "/tmp/pytest_filtered.log"

    expected_count = generate_logfile(original_logfile)
    filters.generic_log_filter(original_logfile, START_TEST, END_TEST, inplace=False, outfile=filtered_logfile)

    # Count how many LOREM IPSUMs in generated file and make sure that matches
    with open(filtered_logfile, "r") as text_file:
        filtered_log = text_file.read()
        assert filtered_log.count(LOREM_IPSUM) == expected_count


@pytest.mark.wip
@pytest.mark.L1
def test_missing_end_generic_log_filter():
    """ Test to make sure the generic log filter is working as expected. """

    original_logfile = "/tmp/pytest_unfiltered.log"
    filtered_logfile = "/tmp/pytest_filtered.log"
    bogus_start = "Bogus Start!!\n"
    bogus_end = "Bogus End!!\n"

    expected_count = generate_logfile(original_logfile)
    filters.generic_log_filter(original_logfile, START_TEST, bogus_end, inplace=False, outfile=filtered_logfile)

    # Count how many LOREM IPSUMs in generated file and make sure that matches
    with open(filtered_logfile, "r") as text_file:
        filtered_log = text_file.read()
        assert filtered_log.count(LOREM_IPSUM) == expected_count

    filters.generic_log_filter(original_logfile, bogus_start, bogus_end, inplace=True, outfile=filtered_logfile)
    with open(filtered_logfile, "r") as text_file:
        filtered_log = text_file.read()
        assert filtered_log.count(LOREM_IPSUM) == expected_count


@pytest.mark.L1
def test_failures_generic_log_filter():
    """ Test to make sure the generic log filter is working as expected. """

    non_existant = "/tmp/DoEsNoTeXiSt.log"

    # Log file doesn't exist
    with pytest.raises(errors.filters.EFilterException):
        filters.generic_log_filter(non_existant, START_TEST, END_TEST, inplace=True)

    # Inplace False and no logfile specified
    with tempfile.NamedTemporaryFile() as tmp:
        with pytest.raises(errors.filters.EFilterException):
            filters.generic_log_filter(tmp.name, START_TEST, END_TEST, inplace=False)


@pytest.mark.L1
def test_regex_log_filter():
    pass
