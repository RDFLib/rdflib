#!/usr/bin/env bash

cd /rdflib
pip install -e .

test_command="nosetests --with-timer --timer-top-n 42 --with-coverage --cover-tests --cover-package=rdflib --cover-html"
echo "Running tests..."
echo "Test command: $test_command"
$test_command