from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Optional, Union, cast

from rdflib.paths import AlternativePath, InvPath, MulPath, Path, SequencePath
from rdflib.term import Node, URIRef

if TYPE_CHECKING:
    from rdflib.graph import Graph

_Pair = tuple[Node, Node]
_Steps = Generator[Union[_Pair, "_Steps"], Optional[_Pair], None]


def evaluate(
    path: Path,
    graph: Graph,
    subj: Optional[Node],
    obj: Optional[Node],
    first: bool = True,
    operator: Optional[type[Path]] = None,
) -> Generator[_Pair, None, None]:
    """Drive suspended path evaluations without nesting Python calls."""
    root = _steps(path, graph, subj, obj, first, operator)
    active = [root]
    # A child that yielded a pair is suspended outside the active stack. Keep
    # ownership until exhaustion so closing the outer iterator also closes it.
    opened = {root: None}
    result: Optional[_Pair] = None
    try:
        while active:
            current = active[-1]
            try:
                step = current.send(result)
            except StopIteration:
                active.pop()
                opened.pop(current, None)
                result = None
                continue
            if isinstance(step, Generator):
                active.append(step)
                opened[step] = None
                result = None
            else:
                active.pop()
                if active:
                    result = step
                else:
                    yield step
                    active.append(root)
                    result = None
    finally:
        for current in reversed(opened):
            current.close()


def _steps(
    path: Union[Path, URIRef],
    graph: Graph,
    subj: Optional[Node],
    obj: Optional[Node],
    first: bool = True,
    operator: Optional[type[Path]] = None,
) -> _Steps:
    if operator is None and isinstance(path, Path):
        # Inherited built-in methods can use the stack; custom overrides must run.
        method = getattr(path.eval, "__func__", None)
        for kind in (InvPath, AlternativePath, SequencePath, MulPath):
            if method is kind.eval:
                operator = kind
                break
    if operator is InvPath:
        child = _steps(cast(InvPath, path).arg, graph, obj, subj)
        while (pair := (yield child)) is not None:
            yield pair[1], pair[0]
    elif operator is AlternativePath:
        for branch in cast(AlternativePath, path).args:
            child = _steps(branch, graph, subj, obj)
            while (pair := (yield child)) is not None:
                yield pair
    elif operator is SequencePath:
        args = cast(SequencePath, path).args
        reverse = subj is None and obj is not None
        index = len(args) - 1 if reverse else 0
        child = _sequence(args, graph, subj, obj, index, reverse)
        while (pair := (yield child)) is not None:
            yield pair
    elif operator is MulPath:
        child = _repeat(cast(MulPath, path), graph, subj, obj, first)
        while (pair := (yield child)) is not None:
            yield pair
    elif isinstance(path, Path):
        yield from path.eval(graph, subj, obj)
    else:
        for source, _, target in graph.triples((subj, path, obj)):
            yield source, target


def _sequence(
    paths: list[Union[Path, URIRef]],
    graph: Graph,
    subj: Optional[Node],
    obj: Optional[Node],
    index: int,
    reverse: bool,
) -> _Steps:
    last = index == (0 if reverse else len(paths) - 1)
    if last:
        child = _steps(paths[index], graph, subj, obj)
    elif reverse:
        child = _steps(paths[index], graph, None, obj)
    else:
        child = _steps(paths[index], graph, subj, None)
    while (pair := (yield child)) is not None:
        if last:
            yield pair
            continue
        if reverse:
            rest = _sequence(paths, graph, subj, pair[0], index - 1, True)
        else:
            rest = _sequence(paths, graph, pair[1], obj, index + 1, False)
        while (joined := (yield rest)) is not None:
            if reverse:
                yield joined[0], pair[1]
            else:
                yield pair[0], joined[1]


def _repeat(
    path: MulPath,
    graph: Graph,
    subj: Optional[Node],
    obj: Optional[Node],
    first: bool,
) -> _Steps:
    done: set[_Pair] = set()
    pair: Optional[_Pair]
    if path.zero:
        if subj is not None or obj is not None:
            if first and (subj is None or obj is None or subj == obj):
                node = subj if subj is not None else obj
                assert node is not None
                pair = node, node
                done.add(pair)
                yield pair
        else:
            for source, target in graph.subject_objects(None):
                for node in (source, target):
                    pair = node, node
                    if pair not in done:
                        done.add(pair)
                        yield pair

    if subj is not None:
        child = _walk(path.path, graph, subj, obj, False, path.more)
        while (pair := (yield child)) is not None:
            if pair not in done:
                done.add(pair)
                yield pair
    elif obj is not None:
        child = _walk(path.path, graph, obj, None, True, path.more)
        while (pair := (yield child)) is not None:
            if pair not in done:
                done.add(pair)
                yield pair
    else:
        starts: set[Node] = set()
        candidates = _steps(path.path, graph, None, None)
        while (pair := (yield candidates)) is not None:
            if not path.more:
                if pair not in done:
                    done.add(pair)
                    yield pair
                continue
            source = pair[0]
            if source in starts:
                continue
            starts.add(source)
            child = _walk(path.path, graph, source, None, False, True)
            while (reachable := (yield child)) is not None:
                if reachable not in done:
                    done.add(reachable)
                    yield reachable


def _walk(
    path: Union[Path, URIRef],
    graph: Graph,
    start: Node,
    target: Optional[Node],
    reverse: bool,
    more: bool,
) -> _Steps:
    visited = {start}
    child = (
        _steps(path, graph, None, start)
        if reverse
        else _steps(path, graph, start, None)
    )
    pending = [child]
    while pending:
        child = pending[-1]
        pair = yield child
        if pair is None:
            pending.pop()
            continue
        node = pair[0] if reverse else pair[1]
        if target is None or node == target:
            yield (node, start) if reverse else (start, node)
        if more and node not in visited:
            visited.add(node)
            child = (
                _steps(path, graph, None, node)
                if reverse
                else _steps(path, graph, node, None)
            )
            pending.append(child)
