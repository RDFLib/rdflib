import abc
import contextlib
import logging
from dataclasses import dataclass
from typing import (
    Any,
    ContextManager,
    Dict,
    Generator,
    Generic,
    Optional,
    Pattern,
    Type,
    TypeVar,
    Union,
)

import pytest
from pytest import ExceptionInfo

AnyT = TypeVar("AnyT")


class ExpectedOutcome(abc.ABC, Generic[AnyT]):
    @abc.abstractmethod
    def check_value(self, result: AnyT) -> None:
        ...

    @contextlib.contextmanager
    @abc.abstractmethod
    def check_raises(self) -> Generator[Optional[ExceptionInfo[Exception]], None, None]:
        ...


@dataclass(frozen=True)
class ValueOutcome(ExpectedOutcome[AnyT]):
    value: AnyT

    def check_value(self, result: AnyT) -> None:
        assert result == self.value

    @contextlib.contextmanager
    def check_raises(self) -> Generator[None, None, None]:
        yield None


@dataclass(frozen=True)
class ExceptionOutcome(ExpectedOutcome, ContextManager[ExceptionInfo[Exception]]):
    type: Type[Exception]
    match: Optional[Union[Pattern[str], str]] = None
    attributes: Optional[Dict[str, Any]] = None

    def check_value(self, result: AnyT) -> None:
        raise RuntimeError("ExceptionResult.check_result should never be called")

    def _check_attributes(self, exception: Exception) -> None:
        if self.attributes is not None:
            for key, value in self.attributes.items():
                logging.debug("checking exception attribute %s=%r", key, value)
                assert hasattr(exception, key)
                assert getattr(exception, key) == value

    @contextlib.contextmanager
    @abc.abstractmethod
    def check_raises(self) -> Generator[ExceptionInfo[Exception], None, None]:
        with pytest.raises(self.type, match=self.match) as catcher:
            yield catcher
        self._check_attributes(catcher.value)

    # def __enter__(self) -> ExceptionInfo[Exception]:
    #     self._exception_info = self._catcher.__enter__()
    #     return self._exception_info

    # def __exit__(
    #     self,
    #     __exc_type: Optional[Type[BaseException]],
    #     __exc_value: Optional[BaseException],
    #     __traceback: Optional[TracebackType],
    # ) -> bool:
    #     result = self._catcher.__exit__(__exc_type, __exc_value, __traceback)
    #     if self._exception_info is not None:
    #         self._check_attributes(self._exception_info.value)
    #     return result
