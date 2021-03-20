# -*- coding: utf-8 -*-
"""
Description:
    This module is meant to test the retry handler logic provided by the utilties portion of epython

Author(s):
    Ray Gomez

Date:
    12/8/20
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from epython import poke

from epython.errors.ssh import SSHError
from epython.handlers import basic_retry_handler, CallbackHandler


class DummyCallbackHandler(CallbackHandler):
    """This is a dummy TestCallbackHandler used purely for unittests."""

    def run_after_exception(self, func_exp=None):
        """This will be mocked in the test."""

    def run_after_function(self, func_result=None):
        """This will be mocked in the test."""


@pytest.mark.L1
@pytest.mark.test_retry_handler
def test_basic_retry_handler_with_retries():
    """Test the basic retry handler without a callback handler to make sure it behaves as expected.

    Steps:
        1) Create a mocked function
        2) Decorate the mocked function that has an SSHError side effect with the basic retry handler
           that retries on SSHError
        3) Validate that the wrapped function fails with an SSHError exception
        4) Validate that the wrapped function was called the same number of times the decorator had
           retries for
    """

    # Need something > 0 to validate the retry mechanism is working
    retries = 3

    # We don't need to wait before retrying for this test
    interval = 0

    func = Mock(side_effect=SSHError())
    dummy_method = basic_retry_handler((SSHError,), retries=retries, interval=interval)(func)

    # A wrapped method should raise the last exception hit when retries are exhausted
    with pytest.raises(SSHError):
        dummy_method()

    assert func.call_count == retries


@pytest.mark.L1
@pytest.mark.test_retry_handler
def test_basic_retry_handler_with_incorrect_exception():
    """Test the basic retry handler that hits an exception that's not in the passed-in list of
    exceptions.

    Steps:
        1) Create a mocked function
        2) Decorate the mocked function that has an DummyException side effect with the basic retry
            handler that retries on SSHError
        3) Validate that the wrapped function fails with a DummyException exception
        4) Validate that the wrapped function was called only once
    """

    class DummyException(Exception):
        """Dummy exception used for test."""

    func = Mock(side_effect=DummyException())
    dummy_method = basic_retry_handler((SSHError,), retries=3, interval=0)(func)

    # A wrapped method should raise the last exception hit when retries are exhausted
    with pytest.raises(DummyException):
        dummy_method()

    assert func.call_count == 1


@pytest.mark.L1
@pytest.mark.test_retry_handler
def test_functional_callback():
    """This test exercises a custom callback that executes after a successful execution of a
    basic_retry_handler wrapped function.

    Steps:
        1) Mock the functional callback of the TestCallbackHandler
        2) Execute the wrapped function
        3) Make sure the return value from the wrapped function is correct
        4) Assert that the callback function `run_after_function` was called only once
    """

    test_callback = DummyCallbackHandler()
    test_callback.run_after_function = Mock(return_value="Yay!")
    func = Mock(return_value="Functional Success")
    dummy_method = basic_retry_handler((SSHError,), callback=test_callback)(func)

    # Execute the method
    assert dummy_method() == "Functional Success", "Failed to get the correct return value"

    # Make sure the wrapped function was called only once
    assert func.call_count == 1

    # Validate mock function was called
    assert test_callback.run_after_function.call_count == 1


@pytest.mark.L1
@pytest.mark.test_retry_handler
def test_exception_callback():
    """This test exercises a custom callback that executes after a failure is captured inside the
    basic_retry_handler

    Steps:
        1) Mock the exception callback of the TestCallbackHandler
        2) Execute the wrapped function
        3) Make sure the wrapped function raises the final exception (SSHError)
        4) Assert the callback function `run_after_exception` call count equals the number of retries
    """

    # Need something > 0 to validate the retry mechanism is working
    retries = 3

    # Setup the Callback handler
    test_callback = DummyCallbackHandler()
    test_callback.run_after_exception = Mock(return_value="Registered Failure!")

    # Setup a mock function to wrap
    func = Mock(side_effect=SSHError())

    # Wrap the mocked function with the basic retry handler
    dummy_method = basic_retry_handler((SSHError,), retries=retries, interval=0,
                                       callback=test_callback)(func)

    # Execute the method
    with pytest.raises(SSHError):
        dummy_method()

    # Validate the function was called the same number of retries
    assert func.call_count == retries, "The mocked function was called a different number of times " \
                                       "than specified with the retries variable"

    # Validate mock function was called
    assert test_callback.run_after_exception.call_count == retries, "The exception callback count " \
                                                                    "does not equal the number of " \
                                                                    "retries"


@pytest.mark.L1
@pytest.mark.test_requests_handler
@pytest.mark.parametrize("test_exception", poke.COMMON_REQUEST_EXCEPTIONS)
def test_requests_retry_handler(test_exception):
    """Test the basic retry handler without a callback handler to make sure it behaves as expected.

    Args:
        test_exception (parameter): The type of exception to raise

    Steps:
        1) Create a mocked function
        2) Decorate the mocked function that has an ConnectionError side effect with the basic retry
           handler that retries on ConnectionError
        3) Validate that the wrapped function fails with an ConnectionError exception
        4) Validate that the wrapped function was called the same number of times the decorator had
           retries for
    """

    # Test URL
    test_url = "http://test.test.test"

    # Need something > 0 to validate the retry mechanism is working
    retries = 3

    # We don't need to wait before retrying for this test
    interval = 0

    # Test GET, POST, PUT, DELETE
    with patch("epython.poke.eprequests.requests") as patched_requests:
        patched_requests.get = MagicMock(side_effect=test_exception())
        patched_requests.post = MagicMock(side_effect=test_exception())
        patched_requests.put = MagicMock(side_effect=test_exception())
        patched_requests.delete = MagicMock(side_effect=test_exception())

        with pytest.raises(test_exception):
            poke.get(test_url, retries=retries, interval=interval)
        assert patched_requests.get.call_count == retries

        with pytest.raises(test_exception):
            poke.post(test_url, retries=retries, interval=interval)
        assert patched_requests.get.call_count == retries

        with pytest.raises(test_exception):
            poke.put(test_url, retries=retries, interval=interval)
        assert patched_requests.get.call_count == retries

        with pytest.raises(test_exception):
            poke.delete(test_url, retries=retries, interval=interval)
        assert patched_requests.get.call_count == retries
