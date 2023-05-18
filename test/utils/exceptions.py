from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from types import TracebackType
from typing import Any, ContextManager, Dict, Optional, Pattern, Type, Union

import pytest
from pytest import ExceptionInfo


@dataclass
class ExceptionChecker(ContextManager[ExceptionInfo[Exception]]):
    type: Type[Exception]
    pattern: Optional[Union[Pattern[str], str]] = None
    attributes: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self._catcher = pytest.raises(self.type, match=self.pattern)
        self._exception_info: Optional[ExceptionInfo[Exception]] = None

    def _check_attributes(self, exception: Exception) -> None:
        if self.attributes is not None:
            for key, value in self.attributes.items():
                logging.debug("checking exception attribute %s=%r", key, value)
                assert hasattr(exception, key)
                assert getattr(exception, key) == value

    def check(self, exception: Exception) -> None:
        logging.debug("checking exception %s/%r", type(exception), exception)
        pattern = self.pattern
        if pattern is not None and not isinstance(pattern, re.Pattern):
            pattern = re.compile(pattern)
        try:
            assert isinstance(exception, self.type)
            if pattern is not None:
                assert pattern.match(f"{exception}")
            self._check_attributes(exception)
        except Exception:
            logging.error("problem checking exception", exc_info=exception)
            raise

    def __enter__(self) -> ExceptionInfo[Exception]:
        self._exception_info = self._catcher.__enter__()
        return self._exception_info

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> bool:
        result = self._catcher.__exit__(__exc_type, __exc_value, __traceback)
        if self._exception_info is not None:
            self._check_attributes(self._exception_info.value)
        return result
