# Copyright (c) 2002, Daniel Krech, http://eikeon.com/
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.
#
#   * Neither the name of Daniel Krech nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Simple Interface for RDF.

SIR is intended to promote a simple interface for RDF that can be used
across serveral different implementations. For the moment further work
on SIR has been deferred until there is a better driving force and
until SIR can have an identity of its own apart from RDFLib.

"""

# Until SIR has a life of its own the following class definitions have
# moved back into RDFLib.
from rdflib.Identifier import Identifier
from rdflib.URIRef import  URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.TripleStore import TripleStore

from rdflib.store.TypeCheck import check_subject, check_predicate, check_object
from rdflib.util import term

from rdflib.exceptions import ParserError

def n3(value):
    if value[0] == '"' and value[-1] == '"':
        return Literal(value[1:-1])
    else:
        return URIRef(value[1:-1])

# Useful RDF constants

# SYNTAX
RDFNS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

TYPE = RDFNS["type"]
PROPERTY = RDFNS["Property"]
STATEMENT = RDFNS["Statement"]
SUBJECT = RDFNS["subject"]
PREDICATE = RDFNS["predicate"]
OBJECT = RDFNS["object"]

FIRST = RDFNS["first"]
REST = RDFNS["rest"]
NIL = RDFNS["nil"]

# SCHEMA
RDFSNS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

CLASS = RDFSNS["Class"]
RESOURCE = RDFSNS["Resource"]
SUBCLASSOF = RDFSNS["subClassOf"]
SUBPROPERTYOF = RDFSNS["subPropertyOf"]
ISDEFINEDBY = RDFSNS["isDefinedBy"]
LABEL = RDFSNS["label"]
COMMENT = RDFSNS["comment"]
RANGE = RDFSNS["range"]
DOMAIN = RDFSNS["domain"]
LITERAL = RDFSNS["Literal"]
CONTAINER = RDFSNS["Container"]
