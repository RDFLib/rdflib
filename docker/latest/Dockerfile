FROM docker.io/library/python:3.12.0-slim@sha256:43a49c9cc2e614468e3d1a903aabe17a97a4c788c76cf5337b5cdc3535b07d4f

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
