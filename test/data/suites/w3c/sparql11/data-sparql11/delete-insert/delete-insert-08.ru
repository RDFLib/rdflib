PREFIX     : <http://example.org/> 

DELETE
 { _:a :p 12 .
   _:a :q ?o .
 }
WHERE {?s :r ?q OPTIONAL { ?q :s ?o } }
