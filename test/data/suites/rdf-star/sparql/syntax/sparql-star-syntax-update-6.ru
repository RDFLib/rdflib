PREFIX : <http://example.com/ns#>

INSERT {
    ?s :r ?o {| :added 'Property :r' |}
} WHERE {
   ?s :p/:q ?o .
}
