FROM docker.io/library/python:3.11.1-slim@sha256:79095e304e31196bad049e74f666508ac81909d201ec9371f9f3cd68fa365cf6

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
