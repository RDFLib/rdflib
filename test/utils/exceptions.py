import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Pattern, Type, Union


@dataclass(frozen=True)
class ExceptionChecker:
    type: Type[Exception]
    pattern: Optional[Union[Pattern[str], str]] = None
    attributes: Optional[Dict[str, Any]] = None

    def check(self, exception: Exception) -> None:
        logging.debug("checking exception %s/%r", type(exception), exception)
        pattern = self.pattern
        if pattern is not None and not isinstance(pattern, re.Pattern):
            pattern = re.compile(pattern)
        try:
            assert isinstance(exception, self.type)
            if pattern is not None:
                assert pattern.match(f"{exception}")
            if self.attributes is not None:
                for key, value in self.attributes.items():
                    logging.debug("checking exception attribute %s=%r", key, value)
                    assert hasattr(exception, key)
                    assert getattr(exception, key) == value
        except Exception:
            logging.error("problem checking exception", exc_info=exception)
            raise
