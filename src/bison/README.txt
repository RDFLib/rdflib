This parser is implemented using the BisonGen format (see references at bottom).  SPARQLParser.c is generated from all the 
.bgen and .bgen.frag files.  The command-line invokation for doing this is:

BisonGen --mode=c SPARQL.bgen

NOTE: The latest version of BisonGen (from CVS) may be required instead of the most package ftp://ftp.4suite.org/pub/BisonGen/

## Bison Gen Resources ##
- Copia article on BisonGen (with links): http://copia.ogbuji.net/blog/2005-04-27/Of_BisonGe
- BisonGen CVS Tree: cvs.4suite.org/viewcvs/BisonGen/