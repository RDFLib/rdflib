# Nested GRAPH
DELETE DATA { 
  GRAPH <G> { 
    <s> <p> <o> .
    GRAPH <G1> { <s> <p1> 'o1' }
  }
}
