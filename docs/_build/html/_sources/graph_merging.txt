.. _graph_merging: Procedures to merge graphs

==============
Merging graphs
==============

Example 1
---------

.. code-block:: python

    import logging

    _logger = logging.getLogger(redfoot_current)

    from rdflib.Graph import Graph

    f = file(args[0], "r")

    pairs = []
    for line in f:
        try:
            line = line.strip()
            source, destination = line.split(" ")
        except ValueError, e:
            _logger.info("Could not split '%s'" % line)
            continue
        source, destination = URIRef(source).abstract(), URIRef(destination).abstract()
        if destination.startswith(source):
            _logger.info("Skipping %s->%s to avoid inf. loop" % (source, destination))
        else:
            pairs.append((source, destination))

    f.close()

    nothing_merged = True

    # merge contexts
    for context in list(redfoot.contexts()):
        for OLD, NEW in pairs:
            if OLD in context.identifier:
                if isinstance(context.identifier, URIRef):
                    identifier = URIRef(context.identifier.replace(OLD, NEW))
                elif isinstance(context.identifier, BNode):
                    identifier = BNode(context.identifier.replace(OLD, NEW))
                else:
                    _logger.warning(
                        "Unexpected identifier type. Skipping context '%s'" \
                            % context.identifier)
                    continue
                new_context = Graph(store=redfoot.store, 
                                    identifier=identifier, 
                                    namespace_manager=redfoot)
                nothing_merged = False
            else:
                new_context = context

            for s, p, o in context:
                ss, pp, oo = s, p, o
                if isinstance(s, URIRef) and OLD in s:
                    ss = URIRef(s.replace(OLD, NEW))
                if isinstance(p, URIRef) and OLD in p:
                    pp = URIRef(p.replace(OLD, NEW))
                if isinstance(o, URIRef) and OLD in o:
                    oo = URIRef(o.replace(OLD, NEW))
                if (ss, pp, oo)!=(s, p, o) or context!=new_context:
                    nothing_merged = False
                    context.remove((s, p, o))
                    new_context.add((ss, pp, oo))

            if new_context!=context:
                redfoot.remove_context(context.identifier)

    if nothing_merged:
        _logger.warning("nothing merged.")

Example 2
---------

.. code-block:: python

    '''
    Tutorial 9 - demonstrate graph operations

    (not really quite graph operations since rdflib cannot merge models like 
    Jena, but this examples shows you can load two different RDF files and 
    rdflib will merge the two together into one model)

    Copyright (C) 2005 Sylvia Wong <sylvia at whileloop dot org>

    This program is free software; you can redistribute it and/or modify it 
    under the terms of the GNU General Public License as published by the 
    Free Software Foundation; either version 2 of the License, or (at your 
    option) any later version.

    This program is distributed in the hope that it will be useful, but 
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
    General Public License for more details.

    You should have received a copy of the GNU General Public License along 
    with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
    '''

    from rdflib.URIRef import URIRef
    from rdflib.Literal import Literal
    from rdflib.BNode import BNode
    from rdflib.Namespace import Namespace

    # Import RDFLib's default TripleStore implementation.
    from rdflib.TripleStore import TripleStore

    inputFileName1 = 'vc-db-3.rdf'
    inputFileName2 = 'vc-db-4.rdf'

    store = TripleStore()
    store.load(inputFileName1)
    store.load(inputFileName2)

    print store.serialize()

vc-db-3.rdf
^^^^^^^^^^^

.. code-block:: xml

    <rdf:RDF
      xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
      xmlns:vCard='http://www.w3.org/2001/vcard-rdf/3.0#'>

      <rdf:Description rdf:about="http://somewhere/JohnSmith/">
        <vCard:FN>John Smith</vCard:FN>
        <vCard:N rdf:parseType="Resource">
    	<vCard:Family>Smith</vCard:Family>
    	<vCard:Given>John</vCard:Given>
        </vCard:N>
      </rdf:Description>
    </rdf:RDF>

vc-db-4.rdf
^^^^^^^^^^^

.. code-block:: xml

    <rdf:RDF
      xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
      xmlns:vCard='http://www.w3.org/2001/vcard-rdf/3.0#'>

      <rdf:Description rdf:about="http://somewhere/JohnSmith/">
        <vCard:FN>John Smith</vCard:FN>
        <vCard:EMAIL rdf:parseType="Resource">
    	<rdf:type rdf:resource="http://www.w3.org/2001/vcard-rdf/3.0#internet"/>
    	<rdf:value>John@somewhere.com</rdf:value>
        </vCard:EMAIL>
      </rdf:Description>
    </rdf:RDF>
