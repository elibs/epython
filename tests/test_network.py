# -*- coding: utf-8 -*-
"""
Description:
    This module is used for testing the internal network module

Author:
    Ray Gomez

Date:
    01/5/20
"""
from unittest.mock import patch
import pytest

from epython import errors
from epython import network


@pytest.mark.L1
@patch('epython.network.requests.get')
def test_wait_for_http(mock_get):
    """ Test the wait_for_http helper method. """

    url = "http://BogusURL"
    status_code = 200

    # Setup mock to test happy path
    mock_get.return_value.status_code = status_code

    network.wait_for_http(url, status_code=status_code, interval=0, timeout=5)
    assert mock_get.call_count == 1

    # Setup mock to test bad status code
    mock_get.return_value.status_code = status_code + 1
    with pytest.raises(errors.util.EPythonUtilException):
        network.wait_for_http(url, status_code=status_code, interval=0, timeout=.1)

    # Setup mock to test requests exception
    mock_get.side_effect = Exception("Mocked Request Exception!")
    with pytest.raises(errors.util.EPythonUtilException):
        network.wait_for_http(url, status_code=status_code, interval=0, timeout=.1)


@pytest.mark.L1
def test_is_port_listening():
    pass


@pytest.mark.L1
def test_wait_for_port_up():
    pass


@pytest.mark.L1
def test_wait_for_port_down():
    pass
