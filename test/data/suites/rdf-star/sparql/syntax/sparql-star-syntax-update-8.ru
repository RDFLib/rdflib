PREFIX : <http://example.com/ns#>

DELETE DATA  {
    :s :p :o1  {| :added 'Test' |}
}
;
INSERT DATA  {
    :s :p :o2  {| :added 'Test' |}
}


