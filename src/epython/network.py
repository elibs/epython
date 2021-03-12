# -*- coding: utf-8 -*-
"""
Description:
    This module contains all of the common util used for a test framework.

Author:
    Ray Gomez

Date:
    12/7/20
"""
import socket
import time

import requests

import errors
from environment import _LOG


def wait_for_http(url, status_code=200, interval=1, timeout=90):
    """ Wait for a specific HTTP Status code from a given url

    Args:
        url (str): The url to wait to resolve
        status_code (int): The HTTP Status code to wait for
        timeout (int): The timeout in seconds (Default: 90)
        interval (int): The interval between retries in seconds (Default: 1)
    """

    _LOG.info("Waiting for url: %s to return status code: %s", url, status_code)
    start_time = time.time()
    while True:
        # Ignore connection issues
        try:
            rsp = requests.get(url)
            if rsp.status_code == status_code:
                return
        # pylint: disable=W0703
        except Exception:
            pass
        # pylint: enable=W0703

        if time.time() - start_time > timeout:
            break
        time.sleep(interval)
    raise errors.util.EPythonUtilException(f"Failed to receive status code: {status_code} from url: "
                                           f"{url} after {timeout} seconds")


def is_port_listening(host, port, wait_interval=2):
    """ Check if a port is up and listening

    Args:
        host (str): The FQDN or the IP address of the system in question
        port (int): The port to check
        wait_interval (int): The interval to wait before determining a port is down

    Returns:

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        socket.setdefaulttimeout(wait_interval)
        result = sock.connect_ex((host, port))
        if result == 0:
            return True
        return False
    # pylint: disable=W0703
    except Exception:
        sock.close()
        return False
    # pylint: enable=W0703
