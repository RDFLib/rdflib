# Docker image for the rdflib test-runner.

# Use the lowest supported Python version to run tests.
FROM python:3.6

COPY requirements.dev.txt .
COPY requirements.txt .

RUN pip install --no-cache -r requirements.dev.txt
RUN pip install --no-cache -r requirements.txt

WORKDIR /rdflib
