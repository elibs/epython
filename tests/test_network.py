# -*- coding: utf-8 -*-
"""
Description:
    This module is used for testing the internal network module

Author:
    Ray Gomez

Date:
    01/5/20
"""
from unittest.mock import patch, MagicMock
import pytest

from epython import errors
from epython import network


@pytest.mark.L1
@patch('epython.network.requests.get')
def test_wait_for_http_status_code(mock_get):
    """ Test the wait_for_http helper method. """

    url = "http://BogusURL"
    status_code = 200

    # Setup mock to test happy path
    mock_get.return_value.status_code = status_code

    network.wait_for_http_status_code(url, status_code=status_code, interval=0, timeout=5)
    assert mock_get.call_count == 1

    # Setup mock to test bad status code
    mock_get.return_value.status_code = status_code + 1
    with pytest.raises(errors.util.EPythonUtilException):
        network.wait_for_http_status_code(url, status_code=status_code, interval=0, timeout=.1)

    # Setup mock to test requests exception
    mock_get.side_effect = Exception("Mocked Request Exception!")
    with pytest.raises(errors.util.EPythonUtilException):
        network.wait_for_http_status_code(url, status_code=status_code, interval=0, timeout=.1)


@pytest.mark.wip
@pytest.mark.L1
@patch('epython.network.socket.socket.connect_ex')
def test_is_port_listening(mock_connect_ex):

    host = "bogus"
    port = 42

    # Happy Path
    mock_connect_ex.return_value = 0
    assert network.is_port_listening(host, port, wait_interval=0)
    assert mock_connect_ex.call_count == 1

    # Negative Path
    mock_connect_ex.return_value = 1
    # Reset call count
    mock_connect_ex.call_count = 0

    assert not network.is_port_listening(host, port, wait_interval=0)
    assert mock_connect_ex.call_count == 1

    # Test Exception
    mock_connect_ex.side_effect = Exception("Bogus stuff")
    assert not network.is_port_listening(host, port, wait_interval=0)


@pytest.mark.wip
@pytest.mark.L1
@patch('epython.network.is_port_listening')
def test_wait_for_port_state(mock_port_listening):

    host = "bogus_host"
    port = 42

    # Test already listening
    state = "Up"
    mock_port_listening.return_value = True
    network.wait_for_port_state(host, port, state, max_wait=10, check_interval=0)
    assert mock_port_listening.call_count == 1

    # Check helper method
    network.wait_for_port_up(host, port, max_wait=10, check_interval=0)
    assert mock_port_listening.call_count == 2

    # Test already down
    state = "DoWn"
    mock_port_listening.return_value = False
    mock_port_listening.call_count = 0
    network.wait_for_port_state(host, port, state, max_wait=10, check_interval=0)
    assert mock_port_listening.call_count == 1

    # Check helper method
    network.wait_for_port_down(host, port, max_wait=10, check_interval=0)
    assert mock_port_listening.call_count == 2

    # Test timer pop for UP state
    state = "UP"
    with pytest.raises(errors.network.EConnectivityException):
        network.wait_for_port_state(host, port, state, max_wait=1, check_interval=0)

    # Test timer pop for DOWN state
    state = "DOWN"
    mock_port_listening.return_value = True
    with pytest.raises(errors.network.EConnectivityException):
        network.wait_for_port_state(host, port, state, max_wait=1, check_interval=0)


@pytest.mark.L1
def test_wait_for_invalid_port_state():
    """ Validates exception thrown when an invalid state is given. """

    host = "bogus"
    port = 42
    invalid_state = "BOGUS_STATE"

    with pytest.raises(errors.network.EInvalidPortState):
        network.wait_for_port_state(host, port, invalid_state)
