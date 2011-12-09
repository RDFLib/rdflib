#!/bin/sh
python3 setup.py build

if [ -d build/py3_testing ]; then
    rm -r build/py3_testing
    echo "Removed py3_testing directory from previous run."
fi

mkdir build/py3_testing
cp -r test build/py3_testing/
cp run_tests.py build/py3_testing/
cp -r build/lib/rdflib build/py3_testing/

cd build/py3_testing

2to3 -wn --no-diffs test
2to3 -wn --no-diffs run_tests.py

python3 run_tests.py
