PREFIX : <http://example.com/ns#>

INSERT {
    << :a :b :c >> ?P :o2  {| ?Y <<:s1 :p1 ?Z>> |}
} WHERE {
   << :a :b :c >> ?P :o1 {| ?Y <<:s1 :p1 ?Z>> |}
}

