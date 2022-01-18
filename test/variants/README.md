# multi variant graphs

This directory containts variants of the same graph encoded in different
formats, or differently in the same format.

The graph that a specific file is a variant of is determined by it's filename.
Files that differ only in file extention but have the same basename are
considered variants of the same graph. Additionally, any suffix that matches
`-variant-[^/]*` is excluded when determening the graph key, so the following
files are all considered variants of the same graph:

```
test/variants/literal_with_lang-variant-control.ttl
test/variants/literal_with_lang.nt
test/variants/literal_with_lang.rdf
test/variants/literal_with_lang.ttl
```

Some additional assertions on graphs can be specified in file names that end
with `-asserts.json`, for details on supported asserts see
`test/test_variants.py`.
