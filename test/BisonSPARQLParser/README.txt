This harness is meant to work against the DAWG test cases:

http://www.w3.org/2001/sw/DataAccess/tests/

The contents should be uncompressed to this directory and test.py should be run from the command line.
Currently it only checks SPARQL parsing.  I.e., it doesn't check against the results of evaluating the parsed
expression, just checks that it parses it.  Any exceptions that are thrown by the generated Bison parser
will be thrown.
