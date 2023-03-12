from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, DefaultDict, Generator, List, Tuple

AuditHookType = Callable[[str, Tuple[Any, ...]], Any]


@dataclass
class AuditHookDispatcher:
    handlers: DefaultDict[str, List[AuditHookType]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def audit(self, name: str, args: Tuple[Any, ...]) -> Any:
        handlers = self.handlers[name]
        for handler in handlers:
            handler(name, args)

    @contextmanager
    def ctx_hook(self, name: str, hook: AuditHookType) -> Generator[None, None, None]:
        self.handlers[name].append(hook)
        try:
            yield None
        finally:
            self.handlers[name].remove(hook)
