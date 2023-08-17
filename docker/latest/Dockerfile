FROM docker.io/library/python:3.11.2-slim@sha256:d0e839882b87135b355361efeb9e9030c9d2a808da06434f4c99eb4009c15e64

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
