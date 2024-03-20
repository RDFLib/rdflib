FROM docker.io/library/python:3.12.2-slim@sha256:5c73034c2bc151596ee0f1335610735162ee2b148816710706afec4757ad5b1e

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
