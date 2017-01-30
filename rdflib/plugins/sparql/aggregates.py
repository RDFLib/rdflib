from rdflib import Literal, XSD

from six import text_type, itervalues
from rdflib.plugins.sparql.evalutils import _eval, NotBoundError, _val
from rdflib.plugins.sparql.operators import numeric
from rdflib.plugins.sparql.datatypes import type_promotion

from rdflib.plugins.sparql.sparql import SPARQLTypeError

from decimal import Decimal

"""
Aggregation functions
"""

class Accumulator(object):
    """abstract base class for different aggregation functions """

    def __init__(self, aggregation):
        self.var = aggregation.res
        self.expr = aggregation.vars
        if not aggregation.distinct:
            self.use_row = self.dont_care
            self.distinct = False
        else:
            self.distinct = aggregation.distinct
            self.seen = set()

    def dont_care(self, row):
        """skips distinct test """
        return True

    def use_row(self, row):
        """tests distinct with set """
        return _eval(self.expr, row) not in self.seen

    def set_value(self, bindings):
        """sets final value in bindings"""
        bindings[self.var] = self.get_value()


class Counter(Accumulator):

    def __init__(self, aggregation):
        super(Counter, self).__init__(aggregation)
        self.value = 0
        if self.expr == "*":
            # cannot eval "*" => always use the full row
            self.eval_row = self.eval_full_row

    def update(self, row, aggregator):
        try:
            val = self.eval_row(row)
        except NotBoundError:
            # skip UNDEF
            return
        self.value += 1
        if self.distinct:
            self.seen.add(val)

    def get_value(self):
        return Literal(self.value)

    def eval_row(self, row):
        return _eval(self.expr, row)

    def eval_full_row(self, row):
        return row

    def use_row(self, row):
        return self.eval_row(row) not in self.seen


def type_safe_numbers(*args):
    if (
            any(isinstance(arg, float) for arg in args)
            and any(isinstance(arg, Decimal) for arg in args)
    ):
        return map(float, args)
    return args


class Sum(Accumulator):

    def __init__(self, aggregation):
        super(Sum, self).__init__(aggregation)
        self.value = 0
        self.datatype = None

    def update(self, row, aggregator):
        try:
            value = _eval(self.expr, row)
            dt = self.datatype
            if dt is None:
                dt = value.datatype
            else:
                dt = type_promotion(dt, value.datatype)
            self.datatype = dt
            self.value = sum(type_safe_numbers(self.value, numeric(value)))
            if self.distinct:
                self.seen.add(value)
        except NotBoundError:
            # skip UNDEF
            pass

    def get_value(self):
        return Literal(self.value, datatype=self.datatype)

class Average(Accumulator):

    def __init__(self, aggregation):
        super(Average, self).__init__(aggregation)
        self.counter = 0
        self.sum = 0
        self.datatype = None

    def update(self, row, aggregator):
        try:
            value = _eval(self.expr, row)
            dt = self.datatype
            self.sum = sum(type_safe_numbers(self.sum, numeric(value)))
            if dt is None:
                dt = value.datatype
            else:
                dt = type_promotion(dt, value.datatype)
            self.datatype = dt
            if self.distinct:
                self.seen.add(value)
            self.counter += 1
        # skip UNDEF or BNode => SPARQLTypeError
        except NotBoundError:
            pass
        except SPARQLTypeError:
            pass

    def get_value(self):
        if self.counter == 0:
            return Literal(0)
        if self.datatype in (XSD.float, XSD.double):
            return Literal(self.sum / self.counter)
        else:
            return Literal(Decimal(self.sum) / Decimal(self.counter))


class Extremum(Accumulator):
    """abstract base class for Minimum and Maximum"""

    def __init__(self, aggregation):
        super(Extremum, self).__init__(aggregation)
        self.value = None
        # DISTINCT would not change the value for MIN or MAX
        self.use_row = self.dont_care

    def set_value(self, bindings):
        if self.value is not None:
            # simply do not set if self.value is still None
            bindings[self.var] = Literal(self.value)

    def update(self, row, aggregator):
        try:
            if self.value is None:
                self.value = _eval(self.expr, row)
            else:
                # self.compare is implemented by Minimum/Maximum
                self.value = self.compare(self.value, _eval(self.expr, row))
        # skip UNDEF or BNode => SPARQLTypeError
        except NotBoundError:
            pass
        except SPARQLTypeError:
            pass


class Minimum(Extremum):

    def compare(self, val1, val2):
        return min(val1, val2, key=_val)


class Maximum(Extremum):

    def compare(self, val1, val2):
        return max(val1, val2, key=_val)


class Sample(Accumulator):
    """takes the first eligable value"""

    def __init__(self, aggregation):
        super(Sample, self).__init__(aggregation)
        # DISTINCT would not change the value
        self.use_row = self.dont_care

    def update(self, row, aggregator):
        try:
            # set the value now
            aggregator.bindings[self.var] =  _eval(self.expr, row)
            # and skip this accumulator for future rows
            del aggregator.accumulators[self.var]
        except NotBoundError:
            pass

    def get_value(self):
        # set None if no value was set
        return None

class GroupConcat(Accumulator):

    def __init__(self, aggregation):
        super(GroupConcat, self).__init__(aggregation)
        # only GROUPCONCAT needs to have a list as accumlator
        self.value = []
        self.separator = aggregation.separator or " "

    def update(self, row, aggregator):
        try:
            value = _eval(self.expr, row)
            self.value.append(value)
            if self.distinct:
                self.seen.add(value)
        # skip UNDEF
        except NotBoundError:
            pass

    def get_value(self):
        return Literal(self.separator.join(text_type(v) for v in self.value))


class Aggregator(object):
    """combines different Accumulator objects"""

    accumulator_classes = {
        "Aggregate_Count": Counter,
        "Aggregate_Sample": Sample,
        "Aggregate_Sum": Sum,
        "Aggregate_Avg": Average,
        "Aggregate_Min": Minimum,
        "Aggregate_Max": Maximum,
        "Aggregate_GroupConcat": GroupConcat,
    }

    def __init__(self, aggregations):
        self.bindings = {}
        self.accumulators = {}
        for a in aggregations:
            accumulator_class = self.accumulator_classes.get(a.name)
            if accumulator_class is None:
                raise Exception("Unknown aggregate function " + a.name)
            self.accumulators[a.res] = accumulator_class(a)

    def update(self, row):
        """update all own accumulators"""
        # SAMPLE accumulators may delete themselves
        # => iterate over list not generator

        for acc in list(itervalues(self.accumulators)):
            if acc.use_row(row):
                acc.update(row, self)

    def get_bindings(self):
        """calculate and set last values"""
        for acc in itervalues(self.accumulators):
            acc.set_value(self.bindings)
        return self.bindings
