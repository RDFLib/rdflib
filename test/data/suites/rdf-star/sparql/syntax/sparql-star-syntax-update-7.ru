PREFIX : <http://example.com/ns#>

DELETE {
    ?s :r ?o {| :added 'Property :r' |}
} WHERE {
   ?s :p ?o {| :q1+ 'ABC' |}
}
