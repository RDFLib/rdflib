<?xml version='1.0'?>
<fragment>  
  <!-- [21]    	FilteredBasicGraphPattern ::= BlockOfTriples? ( Constraint '.'? FilteredBasicGraphPattern )? -->
  <production name='21'>
    <non-terminal>FilteredBasicGraphPattern</non-terminal>
    <rule>
      <code language="c">
        $$ = PyList_New(0);
      </code>      
    </rule>
    <rule>
      <symbol>Triples</symbol>
      <code language="c">
        $$ = PyList_New(1);
        PyList_SET_ITEM($$, 0, $1);
        Py_INCREF($1);
      </code>      
    </rule>            
    <rule>
      <symbol>Triples</symbol>
      <symbol>Constraint</symbol>
      <symbol>DOT</symbol>
      <symbol>FilteredBasicGraphPattern</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Util, "ListPrepend", "OO",PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", $1,$2),$4);
        /*PyList_Append($4, PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", $1,$2));
        Py_INCREF($4);
        $$ = $4;*/
      </code>      
    </rule>            
    <rule>
      <symbol>Triples</symbol>
      <symbol>Constraint</symbol>
      <symbol>FilteredBasicGraphPattern</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Util, "ListPrepend", "OO",PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", $1,$2),$3);
        /*PyList_Append($3, PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", $1,$2));
        Py_INCREF($3);
        $$ = $3;*/
      </code>      
    </rule>            
    <rule>
      <symbol>Constraint</symbol>
      <symbol>DOT</symbol>
      <symbol>FilteredBasicGraphPattern</symbol>
      <code language="c">
        Py_INCREF(Py_None);
        $$ = PyObject_CallMethod(Util, "ListPrepend", "OO",PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", Py_None,$1),$3);
        /*PyList_Append($3, PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", Py_None,$1));
        Py_INCREF($3);
        $$ = $3;*/
      </code>      
    </rule>            
    <rule>
      <symbol>Constraint</symbol>
      <symbol>FilteredBasicGraphPattern</symbol>
      <code language="c">
        Py_INCREF(Py_None);
        $$ = PyObject_CallMethod(Util, "ListPrepend", "OO",PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", Py_None,$1),$2);
        /*PyList_Append($2, PyObject_CallMethod(Triples, "ParsedConstrainedTriples", "OO", Py_None,$1));
        Py_INCREF($2);
        $$ = $2;*/
      </code>      
    </rule>            
  </production>

  <!-- 
       [27] Constraint ::= 'FILTER' ( BrackettedExpression | BuiltInCall | FunctionCall )
  -->
  <production name='27'>
    <non-terminal>Constraint</non-terminal>
    <rule>
      <symbol>FILTER</symbol>
      <symbol>LEFT_PAREN</symbol>
      <symbol>ConditionalOrExpression</symbol>
      <symbol>RIGHT_PAREN</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Filter, "ParsedExpressionFilter", "O", $3);
      </code>      
    </rule>
    <rule>
      <symbol>FILTER</symbol>
      <symbol>BuiltInCall</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Filter, "ParsedFunctionFilter", "O", $2);
      </code>      
    </rule>
    <rule>
      <symbol>FILTER</symbol>
      <symbol>FunctionCall</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Filter, "ParsedFunctionFilter", "O", $2);
      </code>      
    </rule>
  </production>


  <!--
    
    [22] BlockOfTriples ::= TriplesSameSubject ( '.' TriplesSameSubject? )* 
  
  -->
  <production name="22">
    <non-terminal>Triples</non-terminal>
    <rule>      
      <symbol>Triples</symbol>
      <symbol>DOT</symbol>      
      <symbol>TriplesSameSubject</symbol>      
      <code language="c">
	PyList_Append($1, $3);
	Py_INCREF($1);
	$$ = $1;
      </code>
    </rule>            
    <rule>
      <symbol>Triples</symbol>
      <symbol>DOT</symbol>      
    </rule>    
    <rule>
      <symbol>TriplesSameSubject</symbol>
      <code language="c">
        $$ = PyList_New(1);
        /* Steals a reference */
        PyList_SET_ITEM($$, 0, $1);
        Py_INCREF($1);
      </code>
    </rule>    
  </production>

  <!-- 

    [32] TriplesSameSubject ::= VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList

         TriplesSameSubject ::=
                      Var PropertyList                                    |
				GraphTerm PropertyList                        |
				Collection                                             |
				'[' PropertyListNotEmpty ']'                     |
				Collection PropertyList                           |
                      '[' PropertyListNotEmpty ']' PropertyList   |

    -->
  <production name="32">
    <non-terminal>TriplesSameSubject</non-terminal>
    <rule>
      <symbol>Var</symbol>
      <symbol>PropertyListNotEmpty</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Resource, "Resource", "OO", $1,$2);
      </code>
    </rule>            
    <rule>
      <symbol>GraphTerm</symbol>
      <symbol>PropertyListNotEmpty</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Resource, "Resource", "OO", $1,$2);
      </code>
    </rule>    
    <rule>
      <symbol>LEFT_SQUARE</symbol>
      <symbol>PropertyListNotEmpty</symbol>
      <symbol>RIGHT_SQUARE</symbol>
      <symbol>PropertyList</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Resource, "TwiceReferencedBlankNode", "OO", $2,$4);
      </code>
    </rule>    
    <rule>
      <symbol>Collection</symbol>
      <symbol>PropertyListNotEmpty</symbol>
      <code language="c">
        PyObject_CallMethod($1, "setPropertyValueList", "O", $2);
        Py_INCREF($1);        
        $$ = $1;
      </code>
    </rule>
    <rule>
      <symbol>Collection</symbol>      
    </rule>    
  </production>
  
  <!-- 
       [33] PropertyList         ::= PropertyListNotEmpty?
       [34] PropertyListNotEmpty ::= Verb ObjectList ( ';' PropertyList )?

  -->
  <production>
    <non-terminal>PropertyList</non-terminal>
    <rule>
      <symbol>PropertyListNotEmpty</symbol>
    </rule>
    <rule>
      <code language="c">
        $$ = PyList_New(0);
      </code>
    </rule>
  </production>
  <production name="34">
    <non-terminal>PropertyListNotEmpty</non-terminal>
    <rule>
      <symbol>Verb</symbol>
      <symbol>ObjectList</symbol>
      <code language="c">
        $$ = PyList_New(1);
        PyList_SET_ITEM($$, 0, PyObject_CallMethod(Triples, "PropertyValue", "OO", $1,$2));
      </code>
    </rule>   
    <rule>
      <symbol>Verb</symbol>
      <symbol>ObjectList</symbol>
      <symbol>SEMICOLON</symbol>
      <symbol>PropertyList</symbol>      
      <code language="c">
        $$ = PyObject_CallMethod(Util, "ListPrepend", "OO", PyObject_CallMethod(Triples, "PropertyValue", "OO", $1,$2),$4);
      </code>
    </rule>   
  </production>
  
  <!-- 
   [35] ObjectList ::= GraphNode ( ',' ObjectList )?
  -->
  <production name="35">
    <non-terminal>ObjectList</non-terminal>
    <rule>
      <symbol>GraphNode</symbol>
      <code language="c">
        $$ = PyList_New(1);
	PyList_SET_ITEM($$, 0, $1);
	Py_INCREF($1);
      </code>
    </rule>
    <rule>
      <symbol>ObjectList</symbol>
      <symbol>COMMA</symbol>      
      <symbol>GraphNode</symbol>      
      <code language="c">
        PyList_Append($1, $3);
        Py_INCREF($1);
        $$ = $1;
      </code>
    </rule>    
  </production>
  
  <!--

   [40] GraphNode ::= VarOrTerm | TriplesNode
                  ::= Var | GraphTerm | TriplesNode
   -->
  <production name="40">
    <non-terminal>GraphNode</non-terminal>
    <rule>
      <symbol>Var</symbol>
    </rule>
    <rule>
      <symbol>TriplesNode</symbol>
    </rule>
    <rule>
      <symbol>GraphTerm</symbol>
    </rule>    
  </production>
  
  <!-- 

    [36]  Verb ::= VarOrIRIref | 'a'
               ::= Var | IRIref | 'a'
  -->
  <production name="36">
    <non-terminal>Verb</non-terminal>
    <rule>
      <symbol>Var</symbol>
    </rule>
    <rule>
      <symbol>IRIref</symbol>
    </rule>    
    <rule>
      <symbol>A</symbol>
        <code language="c">
          $$ = PyObject_GetAttrString(RDF, "type");
        </code>
    </rule>    
  </production>  
  
  <!--

   [37]  TriplesNode ::= Collection | BlankNodePropertyList
                     ::= Collection | '[' PropertyList ']'
   -->
  <production name="37">
    <non-terminal>TriplesNode</non-terminal>
    <rule>
      <symbol>Collection</symbol>
    </rule>
    <rule>
      <symbol>LEFT_SQUARE</symbol>
      <symbol>PropertyList</symbol>
      <symbol>RIGHT_SQUARE</symbol>
      <code language="c">
        Py_INCREF(Py_None);
        $$ = PyObject_CallMethod(Resource, "Resource", "OO", Py_None,$2);
      </code>
    </rule>
  </production>
  
  <!-- 
       [39] Collection ::= '(' GraphNode+ ')'
   -->
  <production name="39">
    <non-terminal>Collection</non-terminal>
    <rule>
      <symbol>LEFT_PAREN</symbol>
      <symbol>GraphNodeList</symbol>
      <symbol>RIGHT_PAREN</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Resource, "ParsedCollection", "O", $2);
      </code>      
    </rule>
  </production>
  
  <production>
    <non-terminal>GraphNodeList</non-terminal>
    <rule>
      <symbol>GraphNode</symbol>
      <code language="c">
        $$ = PyList_New(1);
        PyList_SET_ITEM($$, 0, $1);
        Py_INCREF($1);
      </code>
    </rule>
    <rule>
      <symbol>GraphNodeList</symbol>
      <symbol>GraphNode</symbol>
      <code language="c">
        PyList_Append($1, $2);
        Py_INCREF($1);
        $$ = $1;
      </code>
    </rule>            
  </production>
  
  <!-- [44] Var ::= '?' VARNAME | $' VARNAME --> 
  <production name="44">
    <non-terminal>Var</non-terminal>
    <rule>
      <symbol>VARNAME</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(rdflib, "Variable", "O", $1);
      </code>
    </rule>
  </production>
  
  <!-- [45] GraphTerm ::= IRIref | 
                          RDFLiteral |
			  NumericLiteral | 
			  '-' NumericLiteral |
			  '+' NumericLiteral | 
			  BooleanLiteral | 
			  BlankNode | 
			  NIL
  -->
  <production name="42">
    <non-terminal>GraphTerm</non-terminal>
    <rule>
      <symbol>IRIref</symbol>
    </rule>
    <rule>
      <symbol>RDFLiteral</symbol>
    </rule>
    <rule>
      <symbol>NumericLiteral</symbol>
    </rule>
    <rule>
      <symbol>PLUS</symbol>
      <symbol>NumericLiteral</symbol>
    </rule>
    <rule>
      <symbol>MINUS</symbol>
      <symbol>NumericLiteral</symbol>
      <!-- Turn it into a number -->
      <code language="c">
        PyObject *negNum = PyNumber_Negative($2);
        $$ = PyObject_CallMethod(rdflib, "Literal", "O", negNum);
        Py_XDECREF(negNum);
      </code>
    </rule>    
    <rule>
      <symbol>BooleanLiteral</symbol>
    </rule>
    <rule>
      <symbol>BlankNode</symbol>
    </rule>
    <rule>
      <symbol>NIL</symbol>
    </rule>    
  </production>

  <!--
  
  [61] NumericLiteral ::= INTEGER | DECIMAL | DOUBLE

  -->
  <production name="61">
    <non-terminal>NumericLiteral</non-terminal>
    <rule>
      <symbol>INTEGER</symbol>
      <!-- Turn it into an integer -->
      <code language="c">
        PyObject *num = PyNumber_Int($1);
	$$ = PyObject_CallMethod(rdflib, "Literal", "O", num);
        Py_XDECREF(num);
      </code>
    </rule>
    <rule>
      <symbol>DECIMAL</symbol>
      <!-- Turn it into a decimal -->
      <code language="c">
        PyObject *num = PyNumber_Float($1);
	$$ = PyObject_CallMethod(rdflib, "Literal", "O", num);
        Py_XDECREF(num);
      </code>
    </rule>
    <rule>
      <symbol>DOUBLE</symbol>
      <code language="c">
        PyObject *num = PyNumber_Float($1);
	$$ = PyObject_CallMethod(rdflib, "Literal", "O", num);
        Py_XDECREF(num);
      </code>
    </rule>
  </production>
  
  <!-- [60] RDFLiteral  ::= String ( LANGTAG | ( '^^' IRIref ) )? -->
  <production name="60">
    <non-terminal>RDFLiteral</non-terminal>
    <rule>
      <symbol>String</symbol>
    </rule>
    <code language="c">
      $$ = PyObject_CallMethod(rdflib, "Literal", "O", $1);
    </code>    
    <rule>
      <symbol>String</symbol>
      <symbol>LANGTAG</symbol>
      <code language="c">
        PyObject *lang = PySequence_GetSlice($2, 1, PyString_GET_SIZE($2));
        $$ = PyObject_CallMethod(rdflib, "Literal", "O", $1,lang);
        Py_XDECREF(lang);
      </code>
    </rule>
    <rule>
      <symbol>String</symbol>
      <symbol>DOUBLE_HAT</symbol>
      <symbol>IRIref</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedDatatypedLiteral", "OO", $1,$3);
      </code>
    </rule>    
  </production>
  
  <!-- [62] BooleanLiteral 	::=  'true' | 'false' -->
  <production name="62">
    <non-terminal>BooleanLiteral</non-terminal>
    <rule>  
      <symbol>TRUE</symbol>
    </rule>
    <rule>
      <symbol>FALSE</symbol>
    </rule>    
  </production>
  
  <!-- [63]   	String ::= STRING_LITERAL1 | 
                           STRING_LITERAL2 | 
			   STRING_LITERAL_LONG1 | 
			   STRING_LITERAL_LONG2     -->
  <production name="63">
    <non-terminal>String</non-terminal>
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_1</symbol>
      <symbol>STRING_LITERAL1</symbol>
      <symbol>STRING_LITERAL_DELIMETER_1</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "O", $2);
      </code>
    </rule>
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_3</symbol>
      <symbol>STRING_LITERAL2</symbol>
      <symbol>STRING_LITERAL_DELIMETER_3</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "O", $2);
      </code>
    </rule>    
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_2</symbol>
      <symbol>STRING_LITERAL_LONG1</symbol>
      <symbol>STRING_LITERAL_DELIMETER_2</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "O", $2);
      </code>
    </rule>
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_4</symbol>
      <symbol>STRING_LITERAL_LONG2</symbol>
      <symbol>STRING_LITERAL_DELIMETER_4</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "O", $2);
      </code>      
    </rule>    
    <!-- Explicit Empty String Rules -->
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_1</symbol>
      <symbol>STRING_LITERAL_DELIMETER_1</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "");
      </code>
    </rule>
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_3</symbol>
      <symbol>STRING_LITERAL_DELIMETER_3</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "");
      </code>
    </rule>    
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_2</symbol>
      <symbol>STRING_LITERAL_DELIMETER_2</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "");
      </code>
    </rule>
    <rule>
      <symbol>STRING_LITERAL_DELIMETER_4</symbol>
      <symbol>STRING_LITERAL_DELIMETER_4</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(Expression, "ParsedString", "");
      </code>      
    </rule>    
    
  </production>
  
  <!-- [66] BlankNode ::= BLANK_NODE_LABEL | ANON -->
  <production name="66">
    <non-terminal>BlankNode</non-terminal>
    <rule>
      <symbol>ANON</symbol>
      <code language="c">
        $$ = PyObject_CallMethod(rdflib, "BNode","");
      </code>
    </rule>
    <rule>
      <symbol>BLANK_NODE_LABEL</symbol>
      <code language="c">
        PyObject *lang = PySequence_GetSlice($1, 2, PyString_GET_SIZE($1));
        $$ = PyObject_CallMethod(rdflib, "BNode", "O",lang);
        Py_XDECREF(lang);                
      </code>
    </rule>
  </production>
</fragment>
