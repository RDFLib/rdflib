<?xml version="1.0"?>
<fragment>
  <states> 
    <exclusive>STRING_MODE_SHORT_1</exclusive>
    <exclusive>STRING_MODE_SHORT_2</exclusive>
    <exclusive>STRING_MODE_LONG_1</exclusive>
    <exclusive>STRING_MODE_LONG_2</exclusive>
    <exclusive>IRI_MODE</exclusive>
  </states>
  
  <!-- Transitions to NON_COMMENT-->
  
  <pattern expression='\x27'>
    <begin>STRING_MODE_SHORT_1</begin>
    <token>STRING_LITERAL_DELIMETER_1</token>
  </pattern>
  <pattern expression='\x27\x27\x27'>
    <begin>STRING_MODE_LONG_1</begin>
    <token>STRING_LITERAL_DELIMETER_2</token>
  </pattern>
  <pattern expression='\x22'>
    <begin>STRING_MODE_SHORT_2</begin>
    <token>STRING_LITERAL_DELIMETER_3</token>
  </pattern>
  <pattern expression='\x22\x22\x22'>
    <begin>STRING_MODE_LONG_2</begin>
    <token>STRING_LITERAL_DELIMETER_4</token>
  </pattern>  
  <pattern expression='&lt;'>
    <begin>IRI_MODE</begin>
    <token>LESS_THAN</token>
  </pattern>  
      
  <pattern expression='{Langtag}'>
    <token>LANGTAG</token>
  </pattern>
  <pattern expression='{Nil}'>
    <token>NIL</token>
  </pattern>
  <pattern expression='{Anon}'>
    <token>ANON</token>
  </pattern>  
  <pattern expression="{PName_LN}">
    <token>PNAME_LN</token>
  </pattern>
  <pattern expression="{PName_NS}">
    <token>PNAME_NS</token>
  </pattern>    
  <pattern expression="{BlankNodeLabel}">
    <token>BLANK_NODE_LABEL </token>
  </pattern>
  <pattern expression="[?$]({NCChar1}|{Digit})({NCChar1}|{Digit}|\u00B7|[\u0300-\u036F])*">
  <!--pattern expression="[?$]{VarName}"-->      
    <token>VARNAME</token>
  </pattern>  
  <pattern expression='{Langtag}'>
    <token>LANGTAG</token>
  </pattern>
  <pattern expression='{Digit}+'>
    <token>INTEGER</token>
  </pattern>
  <pattern expression='{Decimal}'>
    <token>DECIMAL</token>
  </pattern>
  <pattern expression='({Digit}+\.{Digit}*{Exponent})|(\.({Digit})+{Exponent})|(({Digit})+{Exponent})'>
    <token>DOUBLE</token>
  </pattern>

  <scope state='IRI_MODE'>
    <pattern expression='&gt;'>
      <begin>INITIAL</begin>
      <token>GREATER_THAN</token>
    </pattern>    
    <pattern expression="([^&lt;>'{}|^`\u0000-\u0020])*">
      <token>Q_IRI_CONTENT</token>
    </pattern>      
    <pattern expression='=|{S}'>
      <begin>INITIAL</begin>
    </pattern>    
  </scope>
  
  <scope state='STRING_MODE_SHORT_1'>
    <pattern expression='{String_Literal1}'>
      <token>STRING_LITERAL1</token>
    </pattern>
    <pattern expression='\x27'>
      <begin>INITIAL</begin>
      <token>STRING_LITERAL_DELIMETER_1</token>
    </pattern>
  </scope>
  <scope state="STRING_MODE_SHORT_2">
    <pattern expression='{String_Literal2}'>
      <token>STRING_LITERAL2</token>
    </pattern>    
    <pattern expression='\x22'>
      <begin>INITIAL</begin>
      <token>STRING_LITERAL_DELIMETER_3</token>
    </pattern>    
  </scope>
  
  <scope state='STRING_MODE_LONG_1'>
    <pattern expression='{String_Literal_Long1}'>
      <token>STRING_LITERAL_LONG1</token>
    </pattern>
    <pattern expression='\x27\x27\x27'>
      <begin>INITIAL</begin>
      <token>STRING_LITERAL_DELIMETER_2</token>
    </pattern>
  </scope>  
  <scope state='STRING_MODE_LONG_2'>
    <pattern expression='{String_Literal_Long2}'>
      <token>STRING_LITERAL_LONG2</token>
    </pattern>
    <pattern expression='\x22\x22\x22'>
      <begin>INITIAL</begin>
      <token>STRING_LITERAL_DELIMETER_4</token>
    </pattern>
  </scope>  
  
  <!--  single-line comments -->
  <pattern expression='\x23[^\n\r]*(\n|\r|\r\n)?'/>  
  <!-- ignore all whitespace -->
  <pattern expression='{S}'/>
  
  
</fragment>