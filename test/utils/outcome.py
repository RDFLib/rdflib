from __future__ import annotations

import abc
import contextlib
import logging
from collections.abc import Iterable as IterableABC
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    NoReturn,
    Optional,
    Pattern,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

import pytest
from pytest import ExceptionInfo

AnyT = TypeVar("AnyT")

OutcomePrimitive = Union[
    AnyT, Callable[[AnyT], None], "OutcomeChecker[AnyT]", Type[Exception], Exception
]

OutcomePrimitives = Union[
    Iterable[Union[AnyT, Callable[[AnyT], None], "OutcomeChecker[AnyT]"]],
    OutcomePrimitive,
]


class OutcomeChecker(abc.ABC, Generic[AnyT]):
    """
    Validates expected outcomes for tests.

    Useful for parameterized test that can result in values or
    exceptions.
    """

    @abc.abstractmethod
    def check(self, actual: AnyT) -> None:
        """
        Check the actual outcome against the expectation.

        This should run inside the checker's context.

        :param outcome: The actual outcome of the test.
        :raises AssertionError: If the outcome does not match the
            expectation.
        :raises RuntimeError: If this method is called when no outcome
            is expected.
        """
        ...

    @contextlib.contextmanager
    @abc.abstractmethod
    def context(self) -> Generator[Optional[ExceptionInfo[Exception]], None, None]:
        """
        The context in which the test code should run.

        This is necessary for checking exception outcomes.

        :return: A context manager that yields the exception info for
            any exceptions that were raised in this context.
        :raises AssertionError: If the test does not raise an exception
            when one is expected, or if the exception does not match the
            expectation.
        """
        ...

    @classmethod
    def from_primitive(
        cls,
        primitive: OutcomePrimitive[AnyT],
    ) -> OutcomeChecker[AnyT]:
        checker = cls._from_special(primitive)
        if checker is not None:
            return checker
        return ValueChecker(cast(AnyT, primitive))

    @classmethod
    def _from_special(
        cls,
        primitive: Union[
            AnyT,
            Callable[[AnyT], None],
            OutcomeChecker[AnyT],
            Type[Exception],
            Exception,
        ],
    ) -> Optional[OutcomeChecker[AnyT]]:
        if isinstance(primitive, OutcomeChecker):
            return primitive
        if isinstance(primitive, type) and issubclass(primitive, Exception):
            return ExceptionChecker(primitive)
        if isinstance(primitive, Exception):
            return ExceptionChecker(type(primitive), match=primitive.args[0])
        if callable(primitive):
            return CallableChecker(cast(Callable[[AnyT], None], primitive))
        return None

    @classmethod
    def from_primitives(
        cls,
        primitives: OutcomePrimitives[AnyT],
    ) -> OutcomeChecker[AnyT]:
        checker = cls._from_special(primitives)  # type: ignore[arg-type]
        if checker is not None:
            return checker
        if isinstance(primitives, IterableABC) and not isinstance(
            primitives, (str, bytes)
        ):
            primitives = iter(primitives)
            return AggregateChecker([cls.from_primitive(p) for p in primitives])
        return ValueChecker(cast(AnyT, primitives))


@dataclass(frozen=True)
class NoExceptionChecker(OutcomeChecker[AnyT]):
    """
    Base class for checkers that do not expect exceptions.
    """

    @contextlib.contextmanager
    def context(self) -> Generator[None, None, None]:
        yield None


@dataclass(frozen=True)
class AggregateChecker(NoExceptionChecker[AnyT]):
    """
    Validates that the outcome matches all of the given checkers.
    """

    checkers: Sequence[OutcomeChecker[AnyT]]

    def check(self, actual: AnyT) -> None:
        for checker in self.checkers:
            if isinstance(checker, ExceptionChecker):
                raise ValueError(
                    "AggregateChecker should never contain ExceptionChecker"
                )
            checker.check(actual)


@dataclass(frozen=True)
class ValueChecker(NoExceptionChecker[AnyT]):
    """
    Validates that the outcome is a specific value.

    :param value: The expected value.
    """

    expected: AnyT

    def check(self, actual: AnyT) -> None:
        assert self.expected == actual


@dataclass(frozen=True)
class CallableChecker(NoExceptionChecker[AnyT]):
    """
    Validates the outcome with a callable.

    :param callable: The callable that will be called with the outcome
        to validate it.
    """

    callable: Callable[[AnyT], None]

    def check(self, actual: AnyT) -> None:
        self.callable(actual)


@dataclass(frozen=True)
class ExceptionChecker(OutcomeChecker[AnyT]):
    """
    Validates that the outcome is a specific exception.

    :param type: The expected exception type.
    :param match: A regular expression or string that the exception
        message must match.
    :param attributes: A dictionary of attributes that the exception
        must have and their expected values.
    """

    type: Type[Exception]
    match: Optional[Union[Pattern[str], str]] = None
    attributes: Optional[Dict[str, Any]] = None

    def check(self, actual: AnyT) -> NoReturn:
        raise RuntimeError("ExceptionResult.check_result should never be called")

    def _check_attributes(self, exception: Exception) -> None:
        if self.attributes is not None:
            for key, value in self.attributes.items():
                logging.debug("checking exception attribute %s=%r", key, value)
                assert hasattr(exception, key)
                assert getattr(exception, key) == value

    @contextlib.contextmanager
    def context(self) -> Generator[ExceptionInfo[Exception], None, None]:
        with pytest.raises(self.type, match=self.match) as catcher:
            yield catcher
        self._check_attributes(catcher.value)
