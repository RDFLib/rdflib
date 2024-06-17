# multi variant graphs

This directory contains variants of the same graph encoded in different
formats, or differently in the same format.

The graph that a specific file is a variant of is determined by its filename.
Files that differ only in file extensions but have the same basename are
considered variants of the same graph. Additionally, any suffix that matches
`-variant-[^/]*` is excluded when determining the graph key, so the following
files are all considered variants of the same graph:

```
test/variants/literal_with_lang-variant-control.ttl
test/variants/literal_with_lang.nt
test/variants/literal_with_lang.rdf
test/variants/literal_with_lang.ttl
```

Some additional assertions on graphs can be specified in file names that end
with `-asserts.json`, for details on supported asserts see
`test/test_graph/test_variants.py`.
