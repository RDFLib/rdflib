#!/bin/bash

set -v

uri="http://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-3.9.0.tar.gz"

if wget "$uri" &&
       tar -zxf *jena*fuseki*.tar.gz &&
       mv *jena*fuseki*/ fuseki &&
       cd fuseki ; then
    # normal SPARQLStore & Dataset tests:
    bash fuseki-server --port 3030 --debug --update --mem /db &>fuseki.log &
    # SPARQLUpdateStore tests & ConjunctiveGraph endpoint behavior:
    bash fuseki-server --port 3031 --debug --update --memTDB --set tdb:unionDefaultGraph=true /db &>fuseki.log &
    sleep 2
    cd ..
else
    echo "fuseki install failed, skipping... please check URI" >&2
fi
