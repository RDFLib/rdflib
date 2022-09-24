PREFIX : <http://example.com/ns#>

INSERT {
    ?S ?P << :a :b ?O >> {| ?Y ?Z |}
} WHERE {
   ?S ?P << :a :b ?O >> {| ?Y ?Z |}
}
