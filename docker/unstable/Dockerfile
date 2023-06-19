FROM docker.io/library/python:3.11.4-slim@sha256:53a67c012da3b807905559fa59fac48a3a68600d73c5da10c2f0d8adc96dbd01

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
