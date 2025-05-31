# Writing RDFLib Documentation

These docs are generated with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material).

- When writing doc-strings use markdown and google style.
- API Docs are automatically generated with [`mkdocstring`](https://mkdocstrings.github.io).
- See the [supported admonitions here](https://squidfunk.github.io/mkdocs-material/reference/admonitions/#supported-types)

## Building

To build the documentation you can use `mkdocs` from within the poetry environment. To do this, run the following commands:

```bash
# Install poetry venv
poetry install

# Build the docs
poetry run mkdocs build
```

Built HTML docs will be generated in `site/` and API documentation, generated as markdown from doc-strings, will be placed in `docs/apidocs/`.

API Docs are automatically generated with `mkdocstring`

There is also a [tox](https://tox.wiki/en/latest/) environment for building documentation:

```bash
tox -e docs
```

You can check the built documentation with:

```bash
npx -p live-server live-server site/
```

## Development

Run development server with auto-reload on change to code:

```bash
poetry run mkdocs serve
```

## Tables

The tables in `plugin_*.rst` were generated with `plugintable.py`
