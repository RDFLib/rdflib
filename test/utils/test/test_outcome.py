from __future__ import annotations

from contextlib import ExitStack
from typing import Any, Callable, NoReturn, Optional, Type, Union, cast

import pytest

from test.utils.outcome import ExceptionChecker, OutcomeChecker


def _raise(
    what: Union[Type[Exception], Callable[..., Exception]],
    *args: Any,
    **kwargs: Any,
) -> NoReturn:
    if isinstance(what, type) and issubclass(what, Exception):
        raise what(*args, **kwargs)
    elif callable(what):
        what_fn: Callable[..., Exception] = cast(Callable[..., Exception], what)
        raise what_fn(*args, **kwargs)


@pytest.mark.parametrize(
    ("action", "checker", "expected_exception"),
    [
        (lambda: _raise(ValueError), ExceptionChecker(ValueError), None),
        (None, ExceptionChecker(ValueError), RuntimeError),
        (
            lambda: _raise(ValueError, "zzz"),
            OutcomeChecker.from_primitive(ValueError(r"z.z")),
            None,
        ),
        (
            lambda: _raise(ValueError, "zzz"),
            OutcomeChecker.from_primitive(ValueError(r"zaz")),
            AssertionError,
        ),
        (
            lambda: _raise(ValueError, "ae"),
            ExceptionChecker(ValueError, r"ae", {"Not": "Found"}),
            AssertionError,
        ),
        (33, OutcomeChecker.from_primitive(33), None),
        (33, OutcomeChecker.from_primitive(44), AssertionError),
        (
            lambda: _raise(TypeError, "something"),
            OutcomeChecker.from_primitive(TypeError),
            None,
        ),
        (
            lambda: 3,
            OutcomeChecker.from_primitive(TypeError),
            RuntimeError,
        ),
    ],
)
def test_checker(
    action: Union[Callable[[], Any], Any],
    checker: ExceptionChecker,
    expected_exception: Optional[Type[BaseException]],
) -> None:
    """
    Given the action, the checker raises the expected exception, or does
    not raise anything if ``expected_exception`` is None.
    """
    with ExitStack() as xstack:
        if expected_exception is not None:
            xstack.enter_context(pytest.raises(expected_exception))
        with checker.context():
            if callable(action):
                actual_result = action()
            else:
                actual_result = action
            checker.check(actual_result)
