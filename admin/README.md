# Admin Tools

Tools to assist with RDFlib releases, like extracting all merged PRs from GitHub since last release.


## Release procedure

1. merge all PRs for the release
1. pass all tests
1. black everything 
   * use the config, e.g. `black --config black.toml .` in main dir
1. build docs - check for errors/warnings there
1. alter version & date in rdflib/__init__.py
1. update:
    * CHANGELOG.md
    * CONTRIBUTORS
       * use scripts here to generate "PRs since last release"
    * LICENSE (the date)
    * setup.py (the long description)
1. update admin steps (here)
1. push to PyPI
    * `pip3 install twine wheel`
    * `python3 setup.py bdist_wheel sdist`
    * `twine upload ./dist/*`
1. Make GitHub release
    * go to the tagged version, e.g. https://github.com/RDFLib/rdflib/releases/tag/6.0.0
    * edit the release' notes there (likely copy from CHANGELOG)
1. Build readthedocs docco
    * `latest` and `stable` need to be built at least
    * best to make sure the previous (outgoing) release has a number-pegged version, e.g. 5.0.0
1. update the rdflib.dev website page
