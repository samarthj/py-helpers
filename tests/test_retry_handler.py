# StdLib
import time

import pytest

from helpers import RetryHandler


@pytest.mark.xfail(raises=ValueError)
def test_simple():
    @RetryHandler((ValueError,), wait_time=0).wrap
    def value_error():
        raise ValueError("This is a test error")

    value_error()


@pytest.mark.xfail(raises=ValueError)
def test_eventually_fails():
    def callback_for_error(**kwargs):
        print(f"Message from callback: {kwargs}")

    @RetryHandler(
        (ValueError,), max_retries=3, wait_time=0, err_callbacks={"ValueError": (callback_for_error, {"arg3": "arg3"})}
    ).wrap
    def value_error(*args, **kwargs):
        print(f"Message from function: {args}, {kwargs}")
        raise ValueError("This is a test error")

    value_error("arg1", arg2="arg2")


def test_count_retries():
    def callback_for_error(**kwargs):
        print(f"Message from callback: {kwargs}")

    retrier = RetryHandler(
        (ValueError,), max_retries=3, wait_time=0, err_callbacks={"ValueError": (callback_for_error, {})}
    )

    @retrier.wrap
    def test_function(*args, **kwargs):
        print(f"Message from function: {args}, {kwargs}")
        raise ValueError("This is a test error")

    try:
        test_function()
    except ValueError:
        assert retrier.RETRY_ATTEMPTS == 4


def test_error_pass_through():
    def callback_for_error(error_obj):
        assert error_obj
        assert isinstance(error_obj, ValueError)

    retrier = RetryHandler(
        (ValueError,), max_retries=3, wait_time=0, err_callbacks={"ValueError": (callback_for_error, {})}
    )

    @retrier.wrap
    def test_function(*args, **kwargs):
        if kwargs["errors"] > retrier.RETRY_ATTEMPTS:
            raise ValueError("This is a test error")

    test_function(errors=1)
    assert retrier.RETRY_ATTEMPTS == 1


def test_error_multiple_handlers():
    def callback_for_valueerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, ValueError)

    def callback_for_runtimeerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, RuntimeError)

    retrier = RetryHandler(
        (
            ValueError,
            RuntimeError,
        ),
        max_retries=3,
        wait_time=0,
        err_callbacks={
            "ValueError": (callback_for_valueerror, {}),
            "RuntimeError": (callback_for_runtimeerror, {}),
        },
    )

    @retrier.wrap
    def test_function(*args, **kwargs):
        print(retrier.RETRY_ATTEMPTS)
        if retrier.RETRY_ATTEMPTS == 0:
            raise ValueError("This is a value error")
        if retrier.RETRY_ATTEMPTS == 1:
            raise RuntimeError("This is a runtime error")

    test_function(errors=2)
    assert retrier.RETRY_ATTEMPTS == 2


def test_error_early_exit():
    def callback_for_valueerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, ValueError)
        return (True, "fancy_return")

    def callback_for_runtimeerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, RuntimeError)

    retrier = RetryHandler(
        (
            ValueError,
            RuntimeError,
        ),
        max_retries=3,
        wait_time=0,
        err_callbacks={
            "ValueError": (callback_for_valueerror, {}),
            "RuntimeError": (callback_for_runtimeerror, {}),
        },
    )

    @retrier.wrap
    def test_function(*args, **kwargs):
        print(retrier.RETRY_ATTEMPTS)
        if retrier.RETRY_ATTEMPTS == 0:
            raise ValueError("This is a value error")
        if retrier.RETRY_ATTEMPTS == 1:
            raise RuntimeError("This is a runtime error")

    res = test_function(errors=2)
    assert retrier.RETRY_ATTEMPTS == 0
    assert res == "fancy_return"


def test_error_late_exit():
    def callback_for_valueerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, ValueError)

    def callback_for_runtimeerror(error_obj):
        print(error_obj)
        assert error_obj
        assert isinstance(error_obj, RuntimeError)
        return (True, "fancy_return")

    retrier = RetryHandler(
        (
            ValueError,
            RuntimeError,
        ),
        max_retries=3,
        wait_time=0,
        err_callbacks={
            "ValueError": (callback_for_valueerror, {}),
            "RuntimeError": (callback_for_runtimeerror, {}),
        },
    )

    @retrier.wrap
    def test_function(*args, **kwargs):
        print(retrier.RETRY_ATTEMPTS)
        if retrier.RETRY_ATTEMPTS == 0:
            raise ValueError("This is a value error")
        if retrier.RETRY_ATTEMPTS == 1:
            raise RuntimeError("This is a runtime error")

    res = test_function(errors=2)
    assert retrier.RETRY_ATTEMPTS == 1
    assert res == "fancy_return"


def test_success():

    retrier = RetryHandler((ValueError,), max_retries=3, wait_time=0)

    @retrier.wrap
    def test_function(*args, **kwargs):
        if kwargs["errors"] > retrier.RETRY_ATTEMPTS:
            raise ValueError("This is a test error")

    test_function(errors=1)
    assert retrier.RETRY_ATTEMPTS == 1


def test_success_with_wait():

    retrier = RetryHandler((ValueError,), max_retries=3, wait_time=1)

    @retrier.wrap
    def test_function(*args, **kwargs):
        if kwargs["errors"] > retrier.RETRY_ATTEMPTS:
            raise ValueError("This is a test error")

    start_time = time.time()
    test_function(errors=2)
    end_time = time.time()
    assert retrier.RETRY_ATTEMPTS == 2
    assert end_time - start_time >= 2


def test_success_with_return():

    retrier = RetryHandler((ValueError,), max_retries=3, wait_time=0)

    @retrier.wrap
    def test_function(*args, **kwargs):
        if kwargs["errors"] > retrier.RETRY_ATTEMPTS:
            raise ValueError("This is a test error")
        return "my_value1", "my_value2"

    res1, res2 = test_function(errors=1)
    assert res1 == "my_value1"
    assert res2 == "my_value2"
