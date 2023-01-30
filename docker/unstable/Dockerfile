FROM docker.io/library/python:3.11.1-slim@sha256:3d260508893319ee271989fe16c0ddf13c710ec5ce1d0708cda7bc30da8389e7

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
