# Admin Tools

Tools to assist with RDFlib releases, like extracting all merged PRs from GitHub since last release.


## Release procedure

1. merge all PRs for the release
2. pass all tests
    * `python run_tests.py`
3. black everything 
    * use the config, e.g. `black --config black.toml .` in main dir
4. build docs - check for errors/warnings there
    * `python setup.py build_sphinx`
5. alter version & date in rdflib/__init__.py
6. update:
    * CHANGELOG.md
    * CONTRIBUTORS
        * use scripts here to generate "PRs since last release"
        * LICENSE (the date)
    * setup.py (the long description)
7. update admin steps (here)
8. push to PyPI
    * `pip3 install twine wheel`
    * `python3 setup.py bdist_wheel sdist`
    * `twine upload ./dist/*`
9. Make GitHub release
    * go to the tagged version, e.g. https://github.com/RDFLib/rdflib/releases/tag/6.0.0
    * edit the release' notes there (likely copy from CHANGELOG)
10. Build readthedocs docco
    * `latest` and `stable` need to be built at least
    * best to make sure the previous (outgoing) release has a number-pegged version, e.g. 5.0.0
11. update the rdflib.dev website page
12. update the master version to this version + 1
