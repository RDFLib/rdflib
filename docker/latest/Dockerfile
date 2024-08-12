FROM docker.io/library/python:3.12.5-slim@sha256:105e9d85a67db1602e70fa2bbb49c1e66bae7e3bdcb6259344fe8ca116434f74

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
