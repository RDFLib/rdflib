PREFIX : <http://example.com/ns#>

INSERT {
    << :a :b :c >> ?P :o2  {| ?Y ?Z |}
} WHERE {
   << :a :b :c >> ?P :o1 {| ?Y ?Z |}
}

