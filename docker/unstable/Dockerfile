FROM docker.io/library/python:3.11.2-slim@sha256:28e5366ce5c423639950d3962b668730535da08cd235bdacef32171e26cd2b5c

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
