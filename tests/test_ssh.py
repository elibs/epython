# -*- coding: utf-8 -*-
"""
Description:
    This module is used for testing the internal ssh utilities

Author:
    Ray Gomez

Date:
    12/14/20
"""
import os
from unittest.mock import MagicMock, patch

import paramiko
import pytest

import environment
import errors

import ssh


@pytest.fixture(scope="function")
def ssh_zero_interval():
    """ Fixture to provide quick access to changing the ssh retry interval. This is useful for speeding
    up mocked ssh commands. """

    # Save the original interval off
    original_interval = environment.EPYTHON_SSH_RETRY_INTERVAL

    # Set the updated interval to zero
    environment.EPYTHON_SSH_RETRY_INTERVAL = 0

    yield

    # Set the interval back to the original state
    environment.EPYTHON_SSH_RETRY_INTERVAL = original_interval


@pytest.fixture(scope="function")
def ssh_zero_retry():
    """ Fixture to provide quick access to changing the ssh retry count. This is useful for speeding
    up mocked ssh commands. """

    # Save the original interval off
    original_retry_count = environment.EPYTHON_SSH_RETRIES

    # Set the updated interval to zero
    environment.EPYTHON_SSH_RETRIES = 0

    yield

    # Set the interval back to the original state
    environment.EPYTHON_SSH_RETRIES = original_retry_count


@pytest.fixture(scope="module")
def ecdsa_key():
    """ Fixture that generates an ecdsa key and returns the path to the file. """
    path = "/tmp/ssh_host_rsa_key"
    cmd = f"ssh-keygen -t ecdsa -f {path} -N ''"
    os.system(cmd)

    yield path

    # Try and clean up, but ignore any errors as these will get overwritten with
    # future runs
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@pytest.fixture(scope="module")
def rsa_key():
    """ Fixture that generates an rsa key and returns the path to the file. """
    path = "/tmp/ssh_host_ecdsa_key"
    cmd = f"ssh-keygen -t rsa -f {path} -N ''"
    os.system(cmd)
    yield path

    # Try and clean up, but ignore any errors as these will get overwritten with
    # future runs
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@pytest.mark.L1
@pytest.mark.test_ssh
def test_ssh_connect_object(rsa_key):
    """ Basic test that validates the ssh.SSHConnect class """

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"

    mock_set_missing_host_key = MagicMock(return_value=None)

    with patch("paramiko.SSHClient") as mock_client:
        mock_client.return_value = MagicMock()
        mock_client.set_missing_host_key_policy = mock_set_missing_host_key

        with ssh.SSHConnect(host, username, password, pkey=rsa_key):
            pass


@pytest.mark.L1
@pytest.mark.test_ssh
def test_missing_ssh_key():
    """ Basic test that validates the proper error occurs when a missing ssh key is passed in."""

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"
    ssh_key = "/tmp/tHiS_dOeS_nOt_ExIsT"

    with pytest.raises(errors.ssh.SSHKeyNotFound):
        with ssh.SSHConnect(host, username, password, pkey=ssh_key):
            pass


@pytest.mark.L1
@pytest.mark.test_ssh
def test_ecdsa_ssh_key(ecdsa_key):
    """ Basic test that validates an ECDSA key can be used with paramiko. """
    import os

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"

    assert os.path.exists(ecdsa_key)

    # This should just 'work' and not produce any issues
    _ssh_conn = ssh.SSHConnect(host, username, password, pkey=ecdsa_key)

    assert isinstance(_ssh_conn.pkey, paramiko.ecdsakey.ECDSAKey), "The SSH key is not an ECDSA Key!"


@pytest.mark.L1
@pytest.mark.test_ssh
def test_error_connecting():
    """ Basic test that validates the proper error occurs when a missing ssh key is passed in."""

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"

    with patch("paramiko.SSHClient.connect") as mock_connect:
        mock_connect.side_effect = Exception("Bogus Exception")
        with pytest.raises(errors.ssh.SSHError):
            with ssh.SSHConnect(host, username, password, pkey="/tmp/non_existent") as conn:
                pass


@pytest.mark.L1
@pytest.mark.test_ssh
def test_error_closing():
    """ Basic test that validates the proper error occurs when a missing ssh key is passed in."""

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"

    # Mock the opening of context
    with patch("paramiko.SSHClient.connect") as mock_connect:
        mock_connect.return_value = MagicMock()

        # Mock the exiting of context
        with patch("paramiko.SSHClient.close") as mock_close:
            mock_close.side_effect = Exception("Bogus Exception")
            # This shouldn't raise an exception. We don't really care if an exception is raised when
            # we are closing.
            with ssh.SSHConnect(host, username, password) as conn:
                pass


@pytest.mark.L1
@pytest.mark.test_ssh
def test_error_on_stdout_decode(ssh_zero_retry):
    """ Test that validates stdout and fails with the proper exception.

    Args:
        ssh_zero_retry (None): Fixture that provides setting the ssh retries to 0

    Steps:
        1) Mock SSH Class
        2) Mock exception when trying to decode stdout
        3) Validate the proper exception occurs
    """

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"
    cmd = "ls"
    rc = 0

    with patch("ssh.SSHConnect") as mock_ssh:

        stdout = MagicMock()
        stderr = MagicMock()
        stdout.channel.recv_exit_status.return_value = rc

        mock_ssh.return_value.__enter__.return_value.exec_command.return_value = [None, stdout, stderr]

        stdout.read.side_effect = Exception("Bogus Stream Decode Error")

        # Test error on stdout stream decode
        with pytest.raises(errors.ssh.SSHStreamDecodeError):
            _rc, _stdout, _stderr = ssh.execute_command(host, username, password, cmd)


@pytest.mark.L1
@pytest.mark.test_ssh
def test_error_on_stderr_decode(ssh_zero_retry):
    """ Test that validates stderr fails with the proper exception.

    Args:
        ssh_zero_retry (None): Fixture that provides setting the ssh retries to 0

    Steps:
        1) Mock SSH Class
        2) Mock exception when trying to decode stderr
        3) Validate the proper exception occurs
    """

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"
    cmd = "ls"
    rc = 0

    with patch("ssh.SSHConnect") as mock_ssh:

        stdout = MagicMock()
        stderr = MagicMock()
        stdout.channel.recv_exit_status.return_value = rc

        mock_ssh.return_value.__enter__.return_value.exec_command.return_value = [None, stdout, stderr]

        stdout.read().decode().strip.return_value = "Bogus STDOUT"
        stderr.read().decode.side_effect = Exception("Bogus Stream Decode Error")

        # Test error on stderr stream decode
        with pytest.raises(errors.ssh.SSHStreamDecodeError):
            _rc, _stdout, _stderr = ssh.execute_command(host, username, password, cmd)


@pytest.mark.L1
@pytest.mark.test_ssh
def test_error_during_rc_acquisition(ssh_zero_retry):
    """ Test that validates the proper error is raised when we fail to receive a return code.

    Args:
        ssh_zero_retry (None): Fixture that provides setting the ssh retries to 0

    Steps:
        1) Mock SSH Class
        2) Mock exception when trying to retrieve return code
        3) Validate the proper exception occurs
    """

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"
    cmd = "ls"
    rc = 0

    with patch("ssh.SSHConnect") as mock_ssh:
        stdout = MagicMock()
        stderr = MagicMock()
        stdout.channel.recv_exit_status.side_effect = Exception("Bogus SSH Error")

        mock_ssh.return_value.__enter__.return_value.exec_command.return_value = [None, stdout, stderr]

        # Test error on stdout stream decode
        with pytest.raises(errors.ssh.SSHError):
            _rc, _stdout, _stderr = ssh.execute_command(host, username, password, cmd)


@pytest.mark.L1
@pytest.mark.test_ssh
def test_execute_command(ssh_zero_retry):
    """ Basic test that validates the proper error occurs when a missing ssh key is passed in.

    Args:
        ssh_zero_retry (None): Fixture that provides setting the ssh retries to 0

    Steps:
        1) Mock SSH Class
        2) Mock the return values from paramiko
        3) Validate execute_command calls the proper sanitizing methods
        4) Validate execute_command provides the correct values
    """

    host = "localhost"
    username = "bogus_user"
    password = "bogus_pass"
    cmd = "ls"
    rc = 0

    with patch("ssh.SSHConnect") as mock_ssh:

        stdout = MagicMock()
        stdout.channel.recv_exit_status.return_value = rc
        stdout.read().decode().strip = MagicMock(return_value="Bogus STDOUT")

        stderr = MagicMock()
        stderr.read().decode().strip = MagicMock(return_value="Bogus STDERR")

        mock_ssh.return_value.__enter__.return_value.exec_command.return_value = [None, stdout, stderr]
        _rc, _stdout, _stderr = ssh.execute_command(host, username, password, cmd)

        stdout.channel.recv_exit_status.assert_called()

        assert _rc == rc
        assert _stdout == "Bogus STDOUT", "STDOUT didn't match the mock!"
        assert _stderr == "Bogus STDERR", "STDERR didn't match the mock!"


@pytest.mark.L1
@pytest.mark.test_ssh
@patch('ssh.socket.create_connection')
def test_ssh_running(mock_create_connection):
    """ Test the wait for ssh running helper method """

    fqdn = "127.0.0.1"

    # Setup Mock to test happy path
    mock_create_connection.return_value = MagicMock()
    assert ssh.ssh_running(fqdn), "Failed to create a connection!"

    # Setup Mock to test sad path
    mock_create_connection.side_effect = Exception("Bogus Exception")
    assert not ssh.ssh_running(fqdn), "Create connection succeeded!"


@pytest.mark.L1
@pytest.mark.test_ssh
@patch('ssh.ssh_running')
def test_wait_for_ssh(mock_ssh_running):
    """ Test the wait for ssh helper method """

    fqdn = "127.0.0.1"

    # Setup Mock to test happy path
    mock_ssh_running.return_value = True
    ssh.wait_for_ssh(fqdn, timeout=.1, interval=0)
    assert mock_ssh_running.call_count == 1

    # Setup Mock to test sad path
    mock_ssh_running.return_value = False
    with pytest.raises(errors.ssh.SSHTimeoutError):
        ssh.wait_for_ssh(fqdn, timeout=.1, interval=0)
