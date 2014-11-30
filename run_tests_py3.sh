#!/bin/sh
python3 setup.py build

python3 run_tests.py --where=./build/src $@
