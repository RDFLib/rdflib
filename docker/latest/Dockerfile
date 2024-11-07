FROM docker.io/library/python:3.13.0-slim@sha256:2ec5a4a5c3e919570f57675471f081d6299668d909feabd8d4803c6c61af666c

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
