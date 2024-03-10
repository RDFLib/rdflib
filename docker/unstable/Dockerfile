FROM docker.io/library/python:3.12.2-slim@sha256:5c73034c2bc151596ee0f1335610735162ee2b148816710706afec4757ad5b1e

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
