import math
from decimal import Decimal
from functools import partial

import pytest

import rdflib.plugins.sparql.parser as p
from rdflib import XSD, Literal, URIRef, Variable
from rdflib.plugins.sparql.algebra import translatePName, traverse
from rdflib.plugins.sparql.operators import simplify
from rdflib.plugins.sparql.sparql import Prologue, QueryContext, SPARQLError
from test.utils import eq_ as eq


def _eval(e, ctx=None):
    if not ctx:
        ctx = QueryContext()
    try:
        r = e.eval(ctx)
        if isinstance(r, SPARQLError):
            print(r)
            return False
        return r
    except SPARQLError:
        return False


def _translate(e):
    return simplify(traverse(e, visitPost=partial(translatePName, prologue=Prologue())))


def test_regex():
    assert _eval(_translate(p.Expression.parse_string('REGEX("zxcabczxc","abc")')[0]))

    eq(
        bool(_eval(_translate(p.Expression.parse_string('REGEX("zxczxc","abc")')[0]))),
        False,
    )

    assert _eval(
        _translate(p.Expression.parse_string('REGEX("bbbaaaaabbb","ba*b")')[0])
    )


def test_arithmetic():
    eq(_eval(_translate(p.Expression.parse_string("2+3")[0])).value, 5)
    eq(_eval(_translate(p.Expression.parse_string("3-2")[0])).value, 1)

    eq(_eval(_translate(p.Expression.parse_string("2*3")[0])).value, 6)
    eq(_eval(_translate(p.Expression.parse_string("4/2")[0])).value, 2)

    eq(_eval(_translate(p.Expression.parse_string("2+2+2")[0])).value, 6)
    eq(_eval(_translate(p.Expression.parse_string("2-2+2")[0])).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("(2-2)+2")[0])).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("2-(2+2)")[0])).value, -2)

    eq(_eval(_translate(p.Expression.parse_string("2*2*2")[0])).value, 8)
    eq(_eval(_translate(p.Expression.parse_string("4/2*2")[0])).value, 4)
    eq(_eval(_translate(p.Expression.parse_string("8/4*2")[0])).value, 4)
    eq(_eval(_translate(p.Expression.parse_string("8/(4*2)")[0])).value, 1)
    eq(_eval(_translate(p.Expression.parse_string("(2/2)*2")[0])).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("4/(2*2)")[0])).value, 1)

    eq(_eval(_translate(p.Expression.parse_string("2+3*2")[0])).value, 8)
    eq(_eval(_translate(p.Expression.parse_string("(2+3)*2")[0])).value, 10)
    eq(_eval(_translate(p.Expression.parse_string("2+4/2")[0])).value, 4)
    eq(_eval(_translate(p.Expression.parse_string("(2+4)/2")[0])).value, 3)


FLOAT = f"<{XSD.float}>"
INT = f"<{XSD.int}>"
SHORT = f"<{XSD.short}>"


@pytest.mark.parametrize(
    ("expression", "value", "datatype"),
    [
        pytest.param("2*3", 6, XSD.integer, id="integer"),
        pytest.param(f'"3"^^{INT}*"2"^^{SHORT}', 6, XSD.integer, id="integer-subtypes"),
        pytest.param(
            "123456789012345678901234567890*3",
            370370367037037036703703703670,
            XSD.integer,
            id="large-integer",
        ),
        pytest.param("2*1.5", Decimal("3.0"), XSD.decimal, id="decimal"),
        pytest.param("1.5e0*2", 3.0, XSD.double, id="double-first"),
        pytest.param("1.5e0*2*3", 9.0, XSD.double, id="double-chain"),
        pytest.param(f'"2.5"^^{FLOAT}*2', 5.0, XSD.float, id="float"),
        pytest.param("7/2", Decimal("3.5"), XSD.decimal, id="integer-division"),
        pytest.param("7e0/2", 3.5, XSD.double, id="double-division"),
        pytest.param("1e308*10", math.inf, XSD.double, id="overflow"),
        pytest.param("-1e308*10", -math.inf, XSD.double, id="negative-overflow"),
        pytest.param(f"1{'0' * 400}*1e0", math.inf, XSD.double, id="huge-integer"),
        pytest.param("1e0/0", math.inf, XSD.double, id="divide-by-zero"),
        pytest.param("-1e0/0", -math.inf, XSD.double, id="negative-by-zero"),
        pytest.param("1e0/-0e0", -math.inf, XSD.double, id="by-negative-zero"),
        pytest.param(f'"2"^^{FLOAT}/0', math.inf, XSD.float, id="float-by-zero"),
    ],
)
def test_multiplication_and_division_promote_numeric_types(
    expression: str, value: object, datatype: URIRef
) -> None:
    """The result has the promoted type of the operands, as in XPath 3.1
    Functions and Operators, section 4.2: integer times double is a double,
    and a double divided by zero is infinite."""
    result = _eval(_translate(p.Expression.parse_string(expression)[0]))

    assert (result.value, result.datatype) == (value, datatype)


def test_zero_divided_by_zero_is_nan_for_doubles() -> None:
    result = _eval(_translate(p.Expression.parse_string("0e0/0")[0]))

    assert math.isnan(result.value) and result.datatype == XSD.double


@pytest.mark.parametrize(
    "expression",
    [
        pytest.param("1/0", id="integer-by-zero"),
        pytest.param("1.0/0", id="decimal-by-zero"),
        pytest.param(f'"abc"^^<{XSD.integer}>*2', id="ill-typed-integer"),
        pytest.param(f'2*"abc"^^<{XSD.decimal}>', id="ill-typed-decimal"),
        pytest.param(f'"1.5"^^<{XSD.integer}>*3', id="ill-typed-fraction"),
        pytest.param(f'"abc"^^<{XSD.double}>*2', id="ill-typed-double"),
        pytest.param(f'2e0*"abc"^^<{XSD.integer}>', id="ill-typed-with-double"),
        pytest.param(f"1{'0' * 2200}*1{'0' * 2200}", id="too-many-digits"),
    ],
)
def test_multiplication_and_division_errors(expression: str) -> None:
    """Integer and decimal division by zero, ill-typed operands, and an integer
    too long to write are errors, not crashes or strings."""
    assert _eval(_translate(p.Expression.parse_string(expression)[0])) is False


def test_arithmetic_var():
    ctx = QueryContext()
    ctx[Variable("x")] = Literal(2)

    eq(_eval(_translate(p.Expression.parse_string("2+?x")[0]), ctx).value, 4)

    eq(_eval(_translate(p.Expression.parse_string("?x+3")[0]), ctx).value, 5)
    eq(_eval(_translate(p.Expression.parse_string("3-?x")[0]), ctx).value, 1)

    eq(_eval(_translate(p.Expression.parse_string("?x*3")[0]), ctx).value, 6)
    eq(_eval(_translate(p.Expression.parse_string("4/?x")[0]), ctx).value, 2)

    eq(_eval(_translate(p.Expression.parse_string("?x+?x+?x")[0]), ctx).value, 6)
    eq(_eval(_translate(p.Expression.parse_string("?x-?x+?x")[0]), ctx).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("(?x-?x)+?x")[0]), ctx).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("?x-(?x+?x)")[0]), ctx).value, -2)

    eq(_eval(_translate(p.Expression.parse_string("?x*?x*?x")[0]), ctx).value, 8)
    eq(_eval(_translate(p.Expression.parse_string("4/?x*?x")[0]), ctx).value, 4)
    eq(_eval(_translate(p.Expression.parse_string("8/4*?x")[0]), ctx).value, 4)
    eq(_eval(_translate(p.Expression.parse_string("8/(4*?x)")[0]), ctx).value, 1)
    eq(_eval(_translate(p.Expression.parse_string("(?x/?x)*?x")[0]), ctx).value, 2)
    eq(_eval(_translate(p.Expression.parse_string("4/(?x*?x)")[0]), ctx).value, 1)


def test_comparisons():
    eq(bool(_eval(_translate(p.Expression.parse_string("2<3")[0]))), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("2<3.0")[0]))), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("2<3e0")[0]))), True)

    eq(bool(_eval(_translate(p.Expression.parse_string("4<3")[0]))), False)
    eq(bool(_eval(_translate(p.Expression.parse_string("4<3.0")[0]))), False)
    eq(bool(_eval(_translate(p.Expression.parse_string("4<3e0")[0]))), False)

    eq(bool(_eval(_translate(p.Expression.parse_string("2<2.1")[0]))), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("2<21e-1")[0]))), True)

    eq(bool(_eval(_translate(p.Expression.parse_string("2=2.0")[0]))), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("2=2e0")[0]))), True)

    eq(bool(_eval(_translate(p.Expression.parse_string('2="cake"')[0]))), False)


def test_comparisons_var():
    ctx = QueryContext()
    ctx[Variable("x")] = Literal(2)

    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3")[0]), ctx)), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3.0")[0]), ctx)), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3e0")[0]), ctx)), True)

    eq(bool(_eval(_translate(p.Expression.parse_string("?x<2.1")[0]), ctx)), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x<21e-1")[0]), ctx)), True)

    eq(bool(_eval(_translate(p.Expression.parse_string("?x=2.0")[0]), ctx)), True)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x=2e0")[0]), ctx)), True)

    eq(bool(_eval(_translate(p.Expression.parse_string('?x="cake"')[0]), ctx)), False)

    ctx = QueryContext()
    ctx[Variable("x")] = Literal(4)

    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3")[0]), ctx)), False)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3.0")[0]), ctx)), False)
    eq(bool(_eval(_translate(p.Expression.parse_string("?x<3e0")[0]), ctx)), False)


def test_and_or():
    eq(bool(_eval(_translate(p.Expression.parse_string("3>2 && 3>1")[0]))), True)
    eq(
        bool(_eval(_translate(p.Expression.parse_string("3>2 && 3>4 || 2>1")[0]))),
        True,
    )
    eq(
        bool(_eval(_translate(p.Expression.parse_string("2>1 || 3>2 && 3>4")[0]))),
        True,
    )
    eq(
        bool(_eval(_translate(p.Expression.parse_string("(2>1 || 3>2) && 3>4")[0]))),
        False,
    )
