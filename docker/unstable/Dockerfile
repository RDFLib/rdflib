FROM docker.io/library/python:3.11.3-slim@sha256:286f2f1d6f2f730a44108656afb04b131504b610a6cb2f3413918e98dabba67e

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
