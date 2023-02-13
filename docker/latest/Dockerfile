FROM docker.io/library/python:3.11.2-slim@sha256:28e5366ce5c423639950d3962b668730535da08cd235bdacef32171e26cd2b5c

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
