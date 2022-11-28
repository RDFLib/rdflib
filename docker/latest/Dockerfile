FROM docker.io/library/python:3.11.0-slim@sha256:1cd45c5dad845af18d71745c017325725dc979571c1bbe625b67e6051533716c

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
